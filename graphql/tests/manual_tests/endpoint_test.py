import json
import requests

endpoint = "http://0.0.0.0:5000/graphql/"
headers = {}

query = """query {
  getEcho {
    ... on EchoEdge {
      node {
        echo
      }
    }
  }
}"""

r = requests.post(endpoint, json={"query": query}, headers=headers)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    raise Exception(f"Query failed to run with a {r.status_code}.")
