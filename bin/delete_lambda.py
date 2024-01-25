import subprocess
import json

# Gets user input for the prefix of lambdas to delete
prefix = input("Enter Prefix: ")

# Gets ORCA lambda functions with given prefix
get_functions = f"aws lambda list-functions --query 'Functions[] | [?contains(FunctionName, `{prefix}`) == `true`]'"
completed_process = subprocess.run(get_functions, shell=True, capture_output=True)
output = completed_process.stdout
convert = json.loads(output.decode("utf-8").replace("'","'"))

# Deletes ORCA lambda functions with the given prefix
for sub in convert:
    print("Deleting " + sub['FunctionName'])
    lambda_output = sub['FunctionName']
    delete_function = f"aws lambda delete-function --function-name {lambda_output}"
    subprocess.run(delete_function, shell=True, capture_output=True)
