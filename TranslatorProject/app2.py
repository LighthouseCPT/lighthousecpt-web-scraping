import json
import os
from datetime import datetime
import boto3
import pandas as pd
from io import StringIO
from googletrans import Translator


def get_latest_item(items):
    items_with_dates = [(item, datetime.strptime('_'.join(item.split('_')[-2:])[:-5], '%Y-%m-%d_%H-%M-%S'))
                        for item in items]
    latest_item = max(items_with_dates, key=lambda x: x[1])[0]
    return latest_item


def translate_text(val):
    if pd.notnull(val) and not isinstance(val, (int, float)):
        translator = Translator()
        return translator.translate(str(val), dest='zh-cn').text
    return val


def main():
    s3 = boto3.resource('s3')

    en_bucket = s3.Bucket('lighthousecpt-schools-csv')
    cn_bucket = 'lighthousecpt-schools-csv-chinese'
    # Get all CSV files from bucket
    all_files = [obj.key for obj in en_bucket.objects.all() if obj.key.endswith('.csv')]

    # Get unique directories
    directories = set([file.rsplit('/', 1)[0] for file in all_files])

    for directory in directories:
        # Get all files in this directory
        directory_files = [file for file in all_files if file.startswith(directory)]

        if directory_files:
            # Get the latest file in this directory
            latest_file = get_latest_item(directory_files)

            # Only process the latest file
            obj = s3.Object(en_bucket.name, latest_file)

            # Load latest file's data into DataFrame
            data = obj.get().get('Body').read().decode('utf-8')
            df = pd.read_csv(StringIO(data))

            # Translate DataFrame
            df = df.apply(lambda x: x.map(translate_text) if x.dtype == 'object' else x)

            # Save translated DataFrame to a CSV string
            csv_buffer = StringIO()
            df.to_csv(csv_buffer)

            # Write string to Chinese S3 bucket under same key as in the original bucket
            s3.Object(cn_bucket, latest_file).put(Body=csv_buffer.getvalue())


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
