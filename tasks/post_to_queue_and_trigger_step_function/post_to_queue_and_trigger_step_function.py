"""
Name: post_to_queue_and_trigger_step_function.py

Description: Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report, reconcile_orphan_report, and reconcile_phantom_report.
"""
import json
import os
import random
import time
from typing import Any, Dict, Union, List

import boto3
import fastjsonschema
from botocore.client import BaseClient
from cumulus_logger import CumulusLogger
from orca_shared.database import shared_db
from orca_shared.reconciliation import OrcaStatus, update_job
from sqlalchemy import text
from sqlalchemy.future import Engine
from sqlalchemy.sql.elements import TextClause

OS_ENVIRON_TARGET_QUEUE_URL_KEY = "TARGET_QUEUE_URL"
OS_ENVIRON_STEP_FUNCTION_ARN_KEY = "STEP_FUNCTION_ARN"

OUTPUT_JOB_ID_KEY = "jobId"

LOGGER = CumulusLogger(name="ORCA")
# Generating schema validators can take time, so do it once and reuse.
try:
    with open("schemas/input.json", "r") as raw_schema:
        _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
except Exception as ex:
    LOGGER.error(f"Could not build schema validator: {ex}")
    raise


def task(
    records: List[Dict[str, Any]],
    target_queue_url: str,
    step_function_arn: str,
) -> None:
    """
    Posts the records to the target_queue_url, triggering state machine after each one.
    Args:
        records: The records to post.
        target_queue_url: The url of the queue to post the records to.
        step_function_arn: The arn of the step function to trigger.
    Returns: See output.json for details.
    """
    aws_client_sqs = boto3.client("sqs")
    aws_client_sfn = boto3.client("stepfunctions")
    for record in records:
        try:
            process_record(aws_client_sqs, aws_client_sfn, record, target_queue_url, step_function_arn)
        except Exception as record_processing_ex:
            # Do not halt on errors.
            # todo: logging and retries.
            pass


def process_record(
    aws_client_sqs: BaseClient,
    aws_client_sfn: BaseClient,
    record: Dict[str, Any],
    target_queue_url: str,
    step_function_arn: str,
) -> None:
    """
    Posts the records to the target_queue_url, triggering state machine after each one.
    Args:
        aws_client_sqs: Client for communicating with SQS.
        aws_client_sfn: Client for communicating with Step Functions
        record: The record to post.
        target_queue_url: The url of the queue to post the records to.
        step_function_arn: The arn of the step function to trigger.
    Returns: See output.json for details.
    """
    aws_client_sqs.send_message(target_queue_url, record["body"])
    aws_client_sfn.start_execution(step_function_arn)


# Define our delay function
def exponential_delay(base_delay: int, exponential_backoff: int = 2) -> int:
    delay = base_delay + (random.randint(0, 1000) / 1000.0)  # nosec
    time.sleep(delay)
    print(f"Slept for {delay} seconds.")
    return base_delay * exponential_backoff


max_retries = 3
interval_seconds = 1
backoff_rate = 2


def handler(event: Dict[str, Any], context) -> None:
    """
    Lambda handler.
    Receives an events from an SQS queue, sends it to another queue, then triggers an AWS step function.
    Args:
        event: See input.json for details.
        context: An object passed through by AWS. Used for tracking.
    Environment Vars:
        INTERNAL_REPORT_QUEUE_URL (string): The URL of the SQS queue the job came from.
        See shared_db.py's get_configuration for further details.
    Returns: See output.json for details.
    """
    LOGGER.setMetadata(event, context)

    _INPUT_VALIDATE(event)

    try:
        target_queue_url = str(
            os.environ[OS_ENVIRON_TARGET_QUEUE_URL_KEY]
        )
    except KeyError as key_error:
        LOGGER.error(
            f"{OS_ENVIRON_TARGET_QUEUE_URL_KEY} environment value not found."
        )
        raise key_error
    try:
        state_machine_arn = str(
            os.environ[OS_ENVIRON_STEP_FUNCTION_ARN_KEY]
        )
    except KeyError as key_error:
        LOGGER.error(
            f"{OS_ENVIRON_STEP_FUNCTION_ARN_KEY} environment value not found."
        )
        raise key_error

    task(
        event["Records"],
        target_queue_url,
        state_machine_arn
    )
