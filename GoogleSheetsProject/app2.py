import json
import os


def main():
    pass


def lambda_handler(event, context):
    main()


# The following is solely for local testing; AWS Lambda will NOT execute it.
# AWS Lambda will execute the "lambda_handler" function above.
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    event_path = os.path.join(script_dir, 'events/event.json')
    with open(event_path, 'r') as file:
        event_data = json.load(file)
    lambda_handler(event_data, None)
