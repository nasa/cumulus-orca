"""
Name: request_from_archive.py
Description:  Lambda function that makes a restore request from archive bucket for each input file.
"""
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

# noinspection PyPackageRequirements
import boto3

# noinspection PyPackageRequirements
from botocore.client import BaseClient

# noinspection PyPackageRequirements
from botocore.exceptions import ClientError
from orca_shared.recovery import shared_recovery
from run_cumulus_task import run_cumulus_task

DEFAULT_RESTORE_EXPIRE_DAYS = 5
DEFAULT_MAX_REQUEST_RETRIES = 2
DEFAULT_RESTORE_RETRY_SLEEP_SECS = 0

VALID_RESTORE_TYPES = ["Bulk", "Expedited", "Standard"]

OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY = "RESTORE_EXPIRE_DAYS"
OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY = "RESTORE_REQUEST_RETRIES"
OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY = "RESTORE_RETRY_SLEEP_SECS"
OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY = "DEFAULT_RECOVERY_TYPE"
OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY = "STATUS_UPDATE_QUEUE_URL"
OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY = "ORCA_DEFAULT_BUCKET"

EVENT_CONFIG_KEY = "config"
EVENT_INPUT_KEY = "input"

CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY = "defaultBucketOverride"
CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY = "defaultRecoveryTypeOverride"

INPUT_GRANULES_KEY = "granules"

CONFIG_JOB_ID_KEY = "asyncOperationId"
CONFIG_COLLECTION_KEY = "collection"
CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = "s3MultipartChunksizeMb"

GRANULE_GRANULE_ID_KEY = "granuleId"
GRANULE_KEYS_KEY = "keys"
GRANULE_RECOVER_FILES_KEY = "recoverFiles"

# noinspection SpellCheckingInspection
FILE_DEST_BUCKET_KEY = "destBucket"
FILE_KEY_KEY = "key"
FILE_PROCESSED_KEY = "success"  # todo: Rename key in schema to avoid user confusion
FILE_ERROR_MESSAGE_KEY = "errorMessage"
FILE_COMPLETION_TIME_KEY = "completionTime"
FILE_KEY_PATH_KEY = "keyPath"
FILE_REQUEST_TIME_KEY = "requestTime"
FILE_STATUS_ID_KEY = "statusId"
FILE_RESTORE_DESTINATION_KEY = "restoreDestination"
FILE_FILENAME_KEY = "filename"
FILE_LAST_UPDATE_KEY = "lastUpdate"
FILE_MULTIPART_CHUNKSIZE_MB_KEY = "s3MultipartChunksizeMb"

LOGGER = shared_recovery.LOGGER


class RestoreRequestError(Exception):
    """
    Exception to be raised if the restore request fails submission for any of the files.
    """


# noinspection PyUnusedLocal
def task(
    event: Dict, context: object
) -> Dict[str, Any]:  # pylint: disable-msg=unused-argument
    """
    Pulls information from os.environ, utilizing defaults if needed,
    then calls inner_task.
        Args:
            Note that because we are using CumulusMessageAdapter,
            this may not directly correspond to Lambda input.
            event: A dict with the following keys:
                'config' (dict): See schemas/config.json for details.
                'input' (dict): See schemas/input.json for details.
            context: Passed through from AWS and CMA. Unused.
        Environment Vars:
            See docs in handler for details.
        Returns:
            See schemas/output.json for details.
        Raises:
            RestoreRequestError: Thrown if there are errors with the input request.
    """
    # Get max retries for loop back off
    try:
        max_retries = int(os.environ[OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY])
    except KeyError:
        LOGGER.warn(
            f"{OS_ENVIRON_RESTORE_REQUEST_RETRIES_KEY} is not set. "
            f"Defaulting to a value of {DEFAULT_MAX_REQUEST_RETRIES}"
        )
        max_retries = DEFAULT_MAX_REQUEST_RETRIES

    # Get starting sleep value from environment
    try:
        retry_sleep_secs = float(os.environ[OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY])
    except KeyError:
        LOGGER.warn(
            f"{OS_ENVIRON_RESTORE_RETRY_SLEEP_SECS_KEY} is not set. "
            f"Defaulting to a value of {DEFAULT_RESTORE_RETRY_SLEEP_SECS} seconds."
        )
        retry_sleep_secs = DEFAULT_RESTORE_RETRY_SLEEP_SECS

    # Get QUEUE URL
    status_update_queue_url = str(os.environ[OS_ENVIRON_STATUS_UPDATE_QUEUE_URL_KEY])

    # Use the default archive bucket if none is specified for the collection or otherwise given.
    event[EVENT_CONFIG_KEY][
        CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY
    ] = get_default_archive_bucket_name(
        event[EVENT_CONFIG_KEY]
    )  # todo: pass this in as parameter instead of adjusting config dictionary.

    # Get number of days to keep before it sinks back down into inactive storage
    try:
        exp_days = int(os.environ[OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY])
    except KeyError:
        LOGGER.warn(
            f"{OS_ENVIRON_RESTORE_EXPIRE_DAYS_KEY} is not set. Defaulting "
            f"to a value of {DEFAULT_RESTORE_EXPIRE_DAYS} days."
        )
        exp_days = DEFAULT_RESTORE_EXPIRE_DAYS

    # Set the JOB ID if one is not given
    if event[EVENT_CONFIG_KEY][CONFIG_JOB_ID_KEY] is None:
        event[EVENT_CONFIG_KEY][CONFIG_JOB_ID_KEY] = uuid.uuid4().__str__()
        LOGGER.debug(
            f"No bulk job_id sent. Generated value"
            f" {event[EVENT_CONFIG_KEY][CONFIG_JOB_ID_KEY]} for job_id."
        )
    # get the archive recovery type
    recovery_type = get_archive_recovery_type(event["config"])

    # Call the inner task to perform the work of restoring
    return inner_task(  # todo: Split 'event' into relevant properties.
        event,
        max_retries,
        retry_sleep_secs,
        recovery_type,
        exp_days,
        status_update_queue_url,
    )


def get_archive_recovery_type(config: Dict[str, Any]) -> str:
    """
    Returns the archive recovery type from either config or environment variable.
    Must be either 'Bulk', 'Expedited', or 'Standard'.
    Args:
        config: The config dictionary from lambda event.

    Raises:
        KeyError if recovery type is not set.
        ValueError if recovery type value is invalid.
    """

    # Look for config override
    recovery_type = config.get(CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY, None)
    if recovery_type is not None:
        LOGGER.info(
            f"Using restore type of {recovery_type} "
            f"found in the configuration {CONFIG_DEFAULT_RECOVERY_TYPE_OVERRIDE_KEY} key."
        )
    else:
        # Look for default from TF
        recovery_type = os.getenv(OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY, None)
        if recovery_type is not None:
            LOGGER.info(
                f"Using restore type of {recovery_type} "
                f"found in the environment {OS_ENVIRON_DEFAULT_RECOVERY_TYPE_KEY} key."
            )
        else:
            raise KeyError("Recovery type not set.")

    if recovery_type not in VALID_RESTORE_TYPES:
        LOGGER.error(
            f"Invalid restore type value of '{recovery_type}'."
        )
        raise ValueError(
            f"Invalid restore type value of '{recovery_type}'."
        )
    return recovery_type


def get_default_archive_bucket_name(config: Dict[str, Any]) -> str:
    try:
        default_bucket = config[CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY]
        if default_bucket is not None:
            return default_bucket
    except KeyError:
        LOGGER.warn(f"{CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY} is not set.")
    return str(os.environ[OS_ENVIRON_ORCA_DEFAULT_ARCHIVE_BUCKET_KEY])


def inner_task(
    event: Dict,
    max_retries: int,
    retry_sleep_secs: float,
    recovery_type: str,
    restore_expire_days: int,
    status_update_queue_url: str,
) -> Dict[str, Any]:  # pylint: disable-msg=unused-argument
    """
    Task called by the handler to perform the work.
    This task will call the restore_request for each file. Restored files will be kept
    for {exp_days} days before they expire. A restore request will be tried up to {retries} times
    if it fails, waiting {retry_sleep_secs} between each attempt.
        Args:
            Note that because we are using CumulusMessageAdapter,
            this may not directly correspond to Lambda input.
            event: A dict with the following keys:
                'config' (dict): A dict with the following keys:
                    'defaultBucketOverride' (str): The name of the archive bucket
                        from which the files will be restored.
                    'asyncOperationId' (str): The unique identifier used for tracking requests.
                'input' (dict): A dict with the following keys:
                    'granules' (list(dict)): A list of dicts with the following keys:
                        'granuleId' (str): The id of the granule being restored.
                        'keys' (list(dict)): A list of dicts with the following keys:
                            'key' (str): Key to the file within the granule.
                            'destBucket' (str): The bucket the restored file will be moved
                                to after the restore completes.
            max_retries: The maximum number of retries for network operations.
            retry_sleep_secs: The number of time to sleep between retries.
            recovery_type: The Tier for the restore request.
                Valid values are 'Standard'|'Bulk'|'Expedited'.
            restore_expire_days: The number of days the restored file will be accessible
                in the S3 bucket before it expires.
            status_update_queue_url: The URL of the SQS queue to post status to.
        Returns:
            See schemas/output.json
        Raises:
            RestoreRequestError: Thrown if there are errors with the input request.
    """
    # Get the archive bucket from the event
    try:
        archive_bucket = event[EVENT_CONFIG_KEY][
            CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY
        ]
    except KeyError:
        raise RestoreRequestError(
            f"request: {event} does not contain a config value "
            f"for {CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY}"
        )

    # Get the collection's multipart_chunksize from the event.
    collection_multipart_chunksize_mb_str = event[EVENT_CONFIG_KEY].get(
        CONFIG_MULTIPART_CHUNKSIZE_MB_KEY, None
    )
    if collection_multipart_chunksize_mb_str is None:
        LOGGER.info(f"{CONFIG_MULTIPART_CHUNKSIZE_MB_KEY} is not set for config.")
        collection_multipart_chunksize_mb = None
    else:
        collection_multipart_chunksize_mb = int(collection_multipart_chunksize_mb_str)

    # Get the granule array from the event
    granules = event[EVENT_INPUT_KEY][INPUT_GRANULES_KEY]

    # Create the S3 client
    s3 = boto3.client("s3")  # pylint: disable-msg=invalid-name

    # Setup additional information and formatting for the event granule files
    # Setup initial array for the granules processed
    for granule in granules:
        # Initialize the granule copy, file array, and timestamp variables
        files = []
        time_stamp = datetime.now(timezone.utc).isoformat()
        # Loop through the granule files and find the ones to restore
        for keys in granule[GRANULE_KEYS_KEY]:
            # Get the file key (path/filename)
            file_key = keys[FILE_KEY_KEY]
            # get the destination bucket for the file
            destination_bucket_name = keys[FILE_DEST_BUCKET_KEY]

            # Set the initial pending state for the file.
            a_file = {
                FILE_PROCESSED_KEY: False,
                FILE_FILENAME_KEY: os.path.basename(file_key),
                FILE_KEY_PATH_KEY: file_key,
                FILE_RESTORE_DESTINATION_KEY: destination_bucket_name,
                FILE_MULTIPART_CHUNKSIZE_MB_KEY: collection_multipart_chunksize_mb,
                FILE_STATUS_ID_KEY: shared_recovery.OrcaStatus.PENDING.value,
                FILE_REQUEST_TIME_KEY: time_stamp,
                FILE_LAST_UPDATE_KEY: time_stamp,
            }
            file_info = get_s3_object_information(s3, archive_bucket, file_key)
            if file_info is not None:
                if file_info["StorageClass"] == "DEEP_ARCHIVE" and recovery_type == "Expedited":
                    message = f"File '{file_key}' from bucket '{archive_bucket}' " \
                              f"is in storage class '{file_info['StorageClass']}' " \
                              f"which is incompatible with recovery type '{recovery_type}'"
                    LOGGER.error(message)
                    a_file[FILE_PROCESSED_KEY] = True
                    a_file[FILE_STATUS_ID_KEY] = shared_recovery.OrcaStatus.FAILED.value
                    a_file[FILE_ERROR_MESSAGE_KEY] = message
                    a_file[FILE_COMPLETION_TIME_KEY] = time_stamp
                else:
                    LOGGER.info(
                        f"Added {file_key} to the list of files we'll attempt to recover."
                    )
            else:
                message = f"'{file_key}' does not exist in '{archive_bucket}' bucket"
                LOGGER.error(message)
                a_file[FILE_PROCESSED_KEY] = True
                a_file[FILE_STATUS_ID_KEY] = shared_recovery.OrcaStatus.FAILED.value
                a_file[FILE_ERROR_MESSAGE_KEY] = message
                a_file[FILE_COMPLETION_TIME_KEY] = time_stamp
            files.append(a_file)

        # Add file information in the proper format
        granule[GRANULE_RECOVER_FILES_KEY] = files

        # Send initial job and status information to the database queues
        # post to DB-queue. Retry using exponential delay if it fails
        LOGGER.debug("Sending initial job status information to DB QUEUE.")
        job_id = event[EVENT_CONFIG_KEY][CONFIG_JOB_ID_KEY]
        granule_id = granule[GRANULE_GRANULE_ID_KEY]

        for retry in range(max_retries + 1):
            try:
                shared_recovery.create_status_for_job(
                    job_id, granule_id, archive_bucket, files, status_update_queue_url
                )
                break
            except Exception as ex:
                LOGGER.error(
                    f"Ran into error posting to SQS {retry + 1} time(s) with exception '{ex}'"
                )
                # todo: Use backoff code. ORCA-201
                time.sleep(retry_sleep_secs)
                continue
        else:
            message = f"Unable to send message to QUEUE '{status_update_queue_url}'"
            LOGGER.critical(message, exec_info=True)
            raise Exception(message)

        # Process the granules by initiating restoration from archive and updating the
        # database with any failure information.
        process_granule(
            s3,
            granule,
            archive_bucket,
            restore_expire_days,
            max_retries,
            retry_sleep_secs,
            recovery_type,
            job_id,
            status_update_queue_url,
        )

    # Cumulus expects response (payload.granules) to be a list of granule objects.
    # Ideally, we should get a return from process granule with the updated file
    # information.
    return {
        "granules": granules,
        "asyncOperationId": event[EVENT_CONFIG_KEY][CONFIG_JOB_ID_KEY],
    }


def process_granule(
    s3: BaseClient,
    granule: Dict[str, Union[str, List[Dict]]],
    archive_bucket_name: str,
    restore_expire_days: int,
    max_retries: int,
    retry_sleep_secs: float,
    recovery_type: str,
    job_id: str,
    status_update_queue_url: str,
) -> None:  # pylint: disable-msg=unused-argument
    """Call restore_object for the files in the granule_list. Modifies granule for output.
    Args:
        s3: An instance of boto3 s3 client
        granule: A dict with the following keys:
            'granuleId' (str): The id of the granule being restored.
            'recover_files' (list(dict)): A list of dicts with the following keys:
                'keyPath' (str): Key to the file within the granule.
                'success' (bool): Should enter this method set to False.
                    Modified to 'True' by method end.
                'errorMessage' (str): Will be modified if error occurs.


        archive_bucket_name: The S3 archive bucket name.
        restore_expire_days:
            The number of days the restored file will be accessible in the S3 bucket
            before it expires.
        max_retries: The number of attempts to retry a restore_request that failed to submit.
        retry_sleep_secs: The number of seconds to sleep between retry attempts.
        recovery_type: The Tier for the restore request. Valid values are
            'Standard'|'Bulk'|'Expedited'.
        job_id: The unique identifier used for tracking requests.
        status_update_queue_url: The URL of the SQS queue to post status to.

    Raises: RestoreRequestError if any file restore could not be initiated.
    """
    attempt = 1
    granule_id = granule[GRANULE_GRANULE_ID_KEY]

    # Try to restore objects in S3
    while attempt <= max_retries + 1:
        for a_file in granule[GRANULE_RECOVER_FILES_KEY]:
            # Only restore files we have not restored or have not successfully been restored
            if not a_file[FILE_PROCESSED_KEY]:
                LOGGER.debug(f"Attempting to restore object at key "
                             f"'{a_file[FILE_KEY_PATH_KEY]}'...")
                try:
                    restore_object(
                        s3,
                        a_file[FILE_KEY_PATH_KEY],
                        restore_expire_days,
                        archive_bucket_name,
                        attempt,
                        job_id,
                        recovery_type,
                    )

                    # Successful restore
                    a_file[FILE_PROCESSED_KEY] = True

                except ClientError as err:
                    # Set the message for logging and populate file's error message info.
                    LOGGER.error(
                        f"Failed to restore '{a_file[FILE_KEY_PATH_KEY]}' "
                        f"from '{archive_bucket_name}'. "
                        f"Encountered error '{err}'."
                    )
                    a_file[FILE_ERROR_MESSAGE_KEY] = str(err)

        attempt = attempt + 1

        # Only sleep if not on last attempt.
        # todo: Use backoff code. ORCA-201
        if attempt <= max_retries + 1:
            # Check for early completion.
            if all(
                a_file[FILE_PROCESSED_KEY]
                for a_file in granule[GRANULE_RECOVER_FILES_KEY]
            ):
                break
            # No early completion sleep and try again
            time.sleep(retry_sleep_secs)

    # update the status of failed files. Initialize the variables needed
    # for the loop.
    any_error = False
    failed_files = []
    for a_file in granule[GRANULE_RECOVER_FILES_KEY]:
        if not a_file[FILE_PROCESSED_KEY]:
            # if any file failed, the whole granule will fail and the file
            # information should be updated
            any_error = True

            # Update the file status information
            a_file[FILE_STATUS_ID_KEY] = shared_recovery.OrcaStatus.FAILED.value
            a_file[FILE_COMPLETION_TIME_KEY] = datetime.now(timezone.utc).isoformat()

            # send message to DB SQS
            # post to DB-queue. Retry using exponential delay if it fails
            LOGGER.debug(
                "Sending status update information for {filename} to the QUEUE",
                filename=a_file[FILE_FILENAME_KEY],
            )
            for attempt in range(max_retries + 1):
                try:
                    shared_recovery.update_status_for_file(
                        job_id,
                        granule_id,
                        a_file[FILE_FILENAME_KEY],
                        shared_recovery.OrcaStatus.FAILED,
                        a_file[FILE_ERROR_MESSAGE_KEY],
                        status_update_queue_url,
                    )
                    break
                except Exception as ex:
                    LOGGER.error(
                        f"Ran into error posting to SQS {attempt + 1} "
                        f"time(s) with exception '{ex}'"
                    )
                    # todo: Use backoff code. ORCA-201
                    time.sleep(retry_sleep_secs)
                    continue
            else:
                message = f"Unable to send message to QUEUE '{status_update_queue_url}'"
                LOGGER.critical(message, exec_info=True)
                raise Exception(message)

        # Append updated file information to the file array
        failed_files.append(a_file)

    # Update the granule file information
    granule[GRANULE_RECOVER_FILES_KEY] = failed_files

    # If this is reached, that means there is no entry in the db for file's status.
    if any_error:
        LOGGER.error(f"One or more files failed to be requested "
                     f"from '{archive_bucket_name}'. GRANULE: {json.dumps(granule)}")
        raise RestoreRequestError(
            f"One or more files failed to be requested from '{archive_bucket_name}'."
        )


def get_s3_object_information(
        s3_cli: BaseClient, archive_bucket_name: str, file_key: str
                            ) -> Optional[Dict[str, Any]]:
    """Perform a head request to get information about a file in S3.
    Args:
        s3_cli: An instance of boto3 s3 client
        archive_bucket_name: The S3 bucket name
        file_key: The key of the archived object
    Returns:
        None if the object does not exist.
        Otherwise, the dictionary specified in
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3
        .Client.head_object
    """
    try:
        # head_object will fail with a thrown 404 if the object doesn't exist
        # todo: The above case was not covered, and should be considered untested.
        file_info = s3_cli.head_object(Bucket=archive_bucket_name, Key=file_key)
        return file_info
    except ClientError as err:
        LOGGER.error(err)
        code = err.response["Error"]["Code"]
        message = err.response["Error"]["Message"]
        if (
            message == "NoSuchKey" or message == "Not Found" or code == "404"
        ):  # todo: Unit tests say 'Not Found', some online docs say 'NoSuchKey'
            return None
        raise
        # todo: Online docs suggest we could catch
        # 'S3.Client.exceptions.NoSuchKey instead of deconstructing ClientError


def restore_object(
    s3_cli: BaseClient,
    key: str,
    days: int,
    db_archive_bucket_key: str,
    attempt: int,
    job_id: str,
    recovery_type: str,
) -> None:
    # noinspection SpellCheckingInspection
    """Restore an archived S3 object in an Amazon S3 bucket.
    Args:
        s3_cli: An instance of boto3 s3 client.
        key: The key of the archived object being restored.
        days: How many days the restored file will be accessible in the
            S3 bucket before it expires.
        db_archive_bucket_key: The S3 bucket name.
        attempt: The attempt number for logging purposes.
        job_id: The unique id of the job. Used for logging.
        recovery_type: Valid values are
            'Standard'|'Bulk'|'Expedited'.
    Raises:
        ClientError: Raises ClientErrors from restore_object, or if the file is already restored.
    """
    request = {"Days": days, "GlacierJobParameters": {"Tier": recovery_type}}
    # Submit the request
    restore_result = s3_cli.restore_object(
        Bucket=db_archive_bucket_key, Key=key, RestoreRequest=request
    )  # Allow ClientErrors to bubble up.
    if restore_result["ResponseMetadata"]["HTTPStatusCode"] == 200:
        # Will have a non-error path after https://bugs.earthdata.nasa.gov/browse/ORCA-336
        raise ClientError(
            {
                "Error": {
                    "Code": "HTTPStatus: 200",
                    "Message": f"File '{key}' in bucket "
                    f"'{db_archive_bucket_key}' has already been recovered.",
                }
            },
            "restore_object",
        )

    LOGGER.info(
        f"Restore {key} from {db_archive_bucket_key} "
        f"attempt {attempt} successful. Job ID: {job_id}"
    )


def handler(event: Dict[str, Any], context):  # pylint: disable-msg=unused-argument
    """Lambda handler. Initiates a restore_object request from archive for each file of a granule.
    Note that this function is set up to accept a list of granules, (because Cumulus sends a list),
    but at this time, only 1 granule will be accepted.
    This is due to the error handling. If the restore request for any file for a
    granule fails to submit, the entire granule (workflow) fails. If more than one granule were
    accepted, and a failure occurred, at present, it would fail all of them.
    Environment variables can be set to override how many days to keep the restored files, how
    many times to retry a restore_request, and how long to wait between retries.
        Environment Vars:
            RESTORE_EXPIRE_DAYS (int, optional, default = 5): The number of days
                the restored file will be accessible in the S3 bucket before it expires.
            RESTORE_REQUEST_RETRIES (int, optional, default = 3): The number of
                attempts to retry a restore_request that failed to submit.
            RESTORE_RETRY_SLEEP_SECS (int, optional, default = 0): The number of seconds
                to sleep between retry attempts.
            RESTORE_RECOVERY_TYPE (str, optional, default = 'Standard'): the Tier
                for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'.
            CUMULUS_MESSAGE_ADAPTER_DISABLED (str): If set to 'true',
                CumulusMessageAdapter does not modify input.
            STATUS_UPDATE_QUEUE_URL
                The URL of the SQS queue to post status to.
            ORCA_DEFAULT_BUCKET
                The bucket to use if destBucket is not set.
        Args:
            event: See schemas/input.json and combine with knowledge of CumulusMessageAdapter.
            context: An object required by AWS Lambda. Unused.
        Returns:
            A dict with the value at 'payload' matching schemas/output.json
                Combine with knowledge of CumulusMessageAdapter for other properties.
        Raises:
            RestoreRequestError: An error occurred calling restore_object for one or more files.
            The same dict that is returned for a successful granule restore,
            will be included in the message, with 'success' = False for
            the files for which the restore request failed to submit.
    """
    LOGGER.setMetadata(event, context)
    return run_cumulus_task(task, event, context)
