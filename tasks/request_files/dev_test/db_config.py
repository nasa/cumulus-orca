import json
import os

def set_env():
    private_config = None
    if os.path.isfile("private_config.json"):
        try:
            with open("private_config.json") as private_file:
                private_config = json.load(private_file)
                print("private_config: ", private_config)
        except Exception as e:
            self.fail(f"error openening private_config.json. {str(e)}")
    else:
        self.fail("You must define a private_config.json file containing "
                    "DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PW")
    os.environ["DATABASE_HOST"] = private_config["DATABASE_HOST"]
    os.environ["DATABASE_NAME"] = private_config["DATABASE_NAME"]
    os.environ["DATABASE_USER"] = private_config["DATABASE_USER"]
    os.environ["DATABASE_PW"] = private_config["DATABASE_PW"]
