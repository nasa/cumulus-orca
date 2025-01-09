import subprocess
import json

# Gets user input for the prefix of lambdas to delete
prefix = input("Enter Prefix: ")

# Gets ORCA lambda functions with given prefix
get_functions = f"aws lambda list-functions --query 'Functions[] | [?contains(FunctionName, `{prefix}`) == `true`]'"
completed_process = subprocess.run(get_functions, shell=True, capture_output=True)
output = completed_process.stdout
convert = json.loads(output.decode("utf-8").replace("'","'"))

for sub in convert:
    lambda_output = sub['FunctionArn']
    get_tags = f"aws lambda list-tags --resource {lambda_output}"
    tags_process = subprocess.run(get_tags, shell=True, capture_output=True)
    tag_output = tags_process.stdout
    tag_convert = json.loads(tag_output.decode("utf-8").replace("'","'"))
    try:
        # Finds lambdas with the tag application set to ORCA and deletes their log groups to redeploy log groups with specified retention
        for tag in tag_convert:
            for attr in tag_convert[tag]:
                if attr == 'application':
                    if tag_convert[tag]['application'] == 'ORCA':
                        print("Deleting " + sub['FunctionName'] + " log group.")
                        del_log_group = sub['FunctionName']
                        delete_log_group = f"aws logs delete-log-group --log-group-name /aws/lambda/{del_log_group}"
                        subprocess.run(delete_log_group, shell=True, capture_output=True)
    # Throws an error if deletion is interrupted
    except KeyError as ke:
        raise ke
