import json

# specify the path to your json file
file_path = "/Users/bilalakhtar/PycharmProjects/lighthousecpt-web-scraping/SchoolScrapingProject/events/event4.json"

# open the file, read the JSON data
with open(file_path) as json_file:
    input_json = json.load(json_file)

dynamodb_json = {"schools": []}

for school in input_json["schools"]:
    dynamodb_school = {
        "name": {"S": school["name"]},
        "programs": {"SS": school["programs"]},
        "tuition": {"S": school["tuition"]},
        "deadline": {"S": school["deadline"]}
    }

    if isinstance(school["requirement"], dict):
        dynamodb_school["requirement"] = {
            "M": {key: {"S": value} for key, value in school["requirement"].items()}
        }
    else:
        dynamodb_school["requirement"] = {"S": school["requirement"]}

    dynamodb_json["schools"].append(dynamodb_school)

print(json.dumps(dynamodb_json, indent=2))  # pretty print DynamoDB JSON
