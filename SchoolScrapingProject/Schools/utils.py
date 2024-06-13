import json
import os
import re
import traceback
from io import StringIO
import pandas as pd
from openai import OpenAI, AuthenticationError
import boto3
from decimal import Decimal
import numpy as np
from datetime import datetime
from bs4 import NavigableString
from log_config import configure_logger
import requests

logger = configure_logger(__name__)


def float_to_decimal(value):
    if isinstance(value, float):
        if np.isnan(value):  # Handle NaNs
            return None
        elif np.isinf(value):  # Handle Infinity
            return None
        return Decimal(str(value))
    return value


def upload_df_to_dynamodb(df, table_name):
    dynamodb = boto3.resource('dynamodb')

    # Add an 'id' column as the primary key
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'id'}, inplace=True)

    try:
        table = dynamodb.Table(table_name)
        table.load()
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        # create table.
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

        # Convert any NaN or Infinity values to None, and floats to decimals
    df = df.apply(lambda s: s.map(float_to_decimal))

    # Convert DataFrame into list of dictionaries (JSON). Ensure that keys are strings.
    items = [{str(key): value for key, value in item.items()} for item in df.to_dict('records')]

    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def get_latest_item(items):
    items_with_dates = [(item, datetime.strptime('_'.join(item.split('_')[-2:])[:-5], '%Y-%m-%d_%H-%M-%S'))
                        for item in items]
    latest_item = max(items_with_dates, key=lambda x: x[1])[0]
    return latest_item


def get_school_names(directory_name):
    entries = os.listdir(directory_name)
    school_names = []
    for entry in entries:
        if os.path.isdir(os.path.join(directory_name, entry)) and entry[0].isupper():
            school_names.append(entry)

    return school_names


def remove_duplicate_terms(text):
    lines = text.split("\n")
    seen_terms = set()
    clean_lines = []

    for line in lines:
        if "Term:" in line and line in seen_terms:
            continue
        clean_lines.append(line)
        if "Term:" in line:
            seen_terms.add(line)

    return "\n".join(clean_lines)


def extract_content(soup, start_string, end_string, include_end=False, newline_after=None):
    try:
        content = ''
        start = soup.find(string=start_string)
        end = soup.find(string=end_string)

        if not start:
            raise ValueError('Start marker not found in content.')
        if not end:
            raise ValueError('End marker not found in content.')

        for element in start.parent.find_all_next(string=True):
            if element == end:
                if include_end:
                    content += element.strip() + '\n'
                break
            if isinstance(element, NavigableString):
                stripped = element.strip()
                if stripped:
                    content += ' ' + stripped
                    # Newline after each year, if "year" was specified as newline_after.
                    if newline_after == 'year' and re.match(r".*\d{4}$", stripped):
                        content += '\n'

        # clean leading and trailing spaces
        return content.strip()
    except ValueError as e:
        error_message = str(e)
        trace = traceback.format_exc()

        # Construct the message that will be sent on the SNS
        error_log = {
            'error_message': error_message,
            'stack_trace': trace
        }

        # Send the error log to SNS Topic
        send_email('ErrorTopic', f'Error Logs - {datetime.today().strftime("%Y-%m-%d")}', error_log)
        raise  # re-throwing the exception after sending notification


def extract_inner_string(content, start_marker, end_marker, include_end=False):
    try:
        if start_marker not in content and end_marker not in content:
            raise ValueError('Both start and end markers are not found in content.')
        elif start_marker not in content:
            raise ValueError('Start marker not found in content.')
        elif end_marker not in content:
            raise ValueError('End marker not found in content.')
        _, _, after_start = content.partition(start_marker)
        inner_content, _, after_end = after_start.partition(end_marker)
        result_content = start_marker + inner_content
        if include_end:
            result_content += end_marker
        return result_content
    except ValueError as e:
        error_message = str(e)
        trace = traceback.format_exc()

        # Construct the message that will be sent on the SNS
        error_log = {
            'error_message': error_message,
            'stack_trace': trace
        }

        # Send the error log to SNS Topic
        send_email('ErrorTopic', f'Error Logs - {datetime.today().strftime("%Y-%m-%d")}', error_log)
        raise  # re-throwing the exception after sending notification


def download_s3_bucket_contents(bucket_name, local_directory=None):
    s3 = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    if not local_directory:
        local_directory = os.getcwd() + '/s3_download'  # Set to a subfolder in the current directory
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)  # Make sure the directory exists

    for obj in s3_resource.Bucket(bucket_name).objects.all():
        local_file_path = os.path.join(local_directory, obj.key)
        if not os.path.exists(os.path.dirname(local_file_path)):
            os.makedirs(os.path.dirname(local_file_path))
        s3.download_file(bucket_name, obj.key, local_file_path)


def check_api_key(api_key):
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        logger.info('API Key Authentication Successful')
        return api_key
    except AuthenticationError:
        error_msg = 'API Key Authentication Unsuccessful'
        logger.critical(error_msg)
        raise ValueError(error_msg)


def make_request(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, '
                                 'like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        page = requests.get(url, headers=headers)
        logger.debug(f'Successfully made request to: {url}')
        return page
    except requests.RequestException as e:
        logger.error(f'Request error: {e}')
        raise


def filter_with_phrase(text_content, phrase):
    return "\n".join(line for line in text_content.split('\n') if phrase in line)


def sort_df_by_date(df):
    # Assuming df is your DataFrame
    df['Date'] = pd.to_datetime(df['Date'])  # Convert the 'Date' column to datetime type
    df = df.sort_values(by='Date')

    # If you want to reset the index after sorting:
    df = df.reset_index(drop=True)
    return df


def drop_duplicate_columns(df):
    duplicate_column_names = set()

    # Iterate over all columns in DataFrame
    for x in range(df.shape[1]):
        # Select column at xth index.
        col = df.iloc[:, x]

        # Iterate over all columns from (x+1)th index till end
        for y in range(x + 1, df.shape[1]):
            # Select column at yth index.
            other_col = df.iloc[:, y]

            # Check if two columns at x & y index are equal
            if col.equals(other_col):
                duplicate_column_names.add(df.columns.values[y])

    # Drop duplicate columns
    df = df.drop(columns=duplicate_column_names)
    return df


def convert_csv_to_df(csv_string):
    data = StringIO(csv_string)
    df = pd.read_csv(data, sep=',')
    df = df.dropna(how='all', axis=1)
    return df


def send_email(topic_name, subject, message):
    sns = boto3.client('sns')

    # get the topic ARN
    response = sns.create_topic(
        Name=topic_name
    )
    topic_arn = response['TopicArn']

    # Format each item in the message dictionary, separated by blank lines
    formatted_message_parts = [f"{key}:\n{value}" for key, value in message.items()]
    formatted_message = "\n\n".join(formatted_message_parts)

    sns.publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=formatted_message
    )

