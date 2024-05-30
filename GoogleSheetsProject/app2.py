import time
from collections import defaultdict
import gspread
import json
import os
import boto3
import pandas as pd
from io import StringIO
from utils import *
from gspread import WorksheetNotFound


gc = gspread.service_account(filename=json_file)
sh = gc.open("School Info")


def main():
    # Define S3 resource using boto3
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('lighthousecpt-schools-csv')

    # Get all CSV files from bucket
    all_files = sorted([obj.key for obj in bucket.objects.all() if obj.key.endswith('.csv')])

    # Organize files by school name and file type
    files_by_school_and_type = defaultdict(list)
    for file in all_files:
        school_name, school_type = file.split('/')[:2]
        school_type = school_type.replace(f"{school_name}_", "").capitalize()
        files_by_school_and_type[(school_name, school_type)].append(file)

    # Get only the latest file for each school type
    latest_files_by_school = defaultdict(lambda: defaultdict())
    for (school_name, school_type), files in files_by_school_and_type.items():
        latest_files_by_school[school_name][school_type] = get_latest_item(files)

    # Order of school types
    school_type_order = ['Tuition', 'Requirement', 'Deadline']

    # Iterate through each school and file type in specified order
    for school_name, types in latest_files_by_school.items():
        print(school_name)
        for school_type in school_type_order:
            if school_type in types:
                print(school_type)
                file = types[school_type]

                # Only process the latest file
                obj = s3.Object(bucket.name, file)

                # Load latest file's data into DataFrame
                data = obj.get().get('Body').read().decode('utf-8')
                df = pd.read_csv(StringIO(data))

                try:
                    worksheet = sh.worksheet(school_name)
                except WorksheetNotFound:
                    worksheet = sh.add_worksheet(title=school_name, rows=1000, cols=26)

                while True:
                    try:
                        clear_text_and_formatting(sh, worksheet)
                        break  # if no exception was raised, break the loop
                    except gspread.exceptions.APIError:
                        print("Hit Google Sheets API rate limit. Waiting...")
                        time.sleep(5)
                        continue







                print(df)

            # print(df)
            #
            # # Translate DataFrame
            # df = df.applymap(translate_text)
            #
            # # Save translated DataFrame to a CSV string
            # csv_buffer = StringIO()
            # df.to_csv(csv_buffer)
            #
            # # Write string to Chinese S3 bucket under same key as in the original bucket
            # s3.Object(cn_bucket, latest_file).put(Body=csv_buffer.getvalue())


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
