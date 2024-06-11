# School Web Scraping Project for Lighthouse CPT

This repository houses the code for a serverless web scraping system, developed specifically for gathering information about various schools. This project is dedicated for use by the Lighthouse CPT Team.

The system is designed for scalability, enabling easy addition of more colleges and specific pieces of information.

## Overview

The application consists of AWS Lambda functions, developed in Python, responsible for scraping data based on predefined parameters, and storing this data centrally in an Amazon S3 bucket.

## Project Structure

The application follows a modular structure, with each college having its own scraper module within a broader school directory. Each data point of interest (requirement, tuition, and deadline) for individual colleges also has separate Python script under specified directories. The project directory structure is:

```
.
├── README.md
├── app.py
├── requirements.txt
├── Schools
│   └── SchoolName
|       ├── requirement
|       |   └── requirement.py
|       ├── tuition
|       |   └── tuition.py
|       └── deadline
|           └── deadline.py
└── init.py
```
-  `app.py`: The main AWS Lambda handler. Maps given schools to their respective scraping functions. Includes the functionality to specify which schools to scrape data from.
-  `Schools`: This directory contains individual directories for each school.
-  `SchoolName`: Represents individual school directory and sub-directories for each specific data point to be scraped (`requirement`, `tuition`, `deadline`). Each of these data point directories has its own Python script for data scraping (`requirement.py`, `tuition.py`, `deadline.py`)
-  `requirements.txt`: Contains necessary Python dependencies needed for the project.

## How to Run Locally

You can use the AWS SAM CLI to invoke Lambda functions locally. 

```bash
sam local invoke SamDemoFunction -e events/event.json
```

Replace `SamDemoFunction` with the logical id of your function as defined in AWS SAM template and `events/event.json` stands for JSON event data file that acts as input for Lambda function during local testing.

## Logging  

The application uses Python's in-built logging module. Log streams from AWS Lambda are automatically sent to CloudWatch Logs enabling an easy way to monitor and troubleshoot your Lambda function.

## Dependencies

The project depends on several Python packages including `requests`, `bs4` (BeautifulSoup), `pandas`, and `boto3`. These dependencies are listed in the `requirements.txt` file.

## Deployment

Deployment specifics will depend on your team's practices. It is common to use services like AWS SAM or the Serverless Framework to manage application deployment. 

## Contributions

Contributions are limited to members of the Lighthouse CPT team.

## Caution

The scraping scripts in this repository should be used responsibly and in accordance with colleges' data scraping policies. Please respect the terms of service and `robots.txt` files of each website.

## Contact

For any further questions or suggestions regarding the repository, please connect with the repository administrators.
