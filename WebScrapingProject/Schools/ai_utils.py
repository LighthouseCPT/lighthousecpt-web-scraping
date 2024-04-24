from io import StringIO
import pandas as pd
from openai import OpenAI
from log_config import configure_logger

logging = configure_logger(__name__)

# client = OpenAI(api_key="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") MINE
client = OpenAI(api_key="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")


def openai_prompter(prompt, model=None, temperature=None):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": f"{prompt}"}
            ],
            temperature=temperature
        )
        response = completion.choices[0].message.content
        msg = f"Successfully generated response: {response}"
        logging.debug(msg)
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Unable to generate response: {str(e)}")


def get_confident_response(prompt, identical_responses_needed=2, max_attempts=10, model=None, temperature=None):
    responses = []

    for _ in range(max_attempts):
        current_response = openai_prompter(prompt, model=model, temperature=temperature)
        responses.append(current_response)

        if responses.count(current_response) == identical_responses_needed:
            break
    else:
        error_msg = f"The script did not produce matching responses in the given {max_attempts} attempts."
        logging.error(error_msg)
        raise Exception(error_msg)

    success_msg = f"The responses matched {identical_responses_needed} times: {current_response}"
    logging.info(success_msg)
    return current_response


def extract_dates_to_csv(text):
    prompt = (f"I have a set of academic dates and schedules that I extracted from the internet or a PDF. "
              f"I need to identify only the "
              f"program start and end dates, along with application deadlines (if any). This information is intended "
              f"for display on a study abroad agency website to assist prospective students. "
              f"Depending on the content of the extracted text, "
              f"feel free to use one or more of these columns: 'Term', 'Date', 'Session', 'Type', 'Program', "
              f"or 'Description'"
              f". Each unique entry should be on a new line with elements separated by commas. "
              f"Each date should be in 'YYYY-MM-DD' format. For terms, use the full "
              f"format like 'Fall 2023', 'Spring 2024' etc. Avoid any additional bibliographical conversation or "
              f"content"
              f"in the response. Here is the text: \n'{text}'")
    logging.debug(f"Returning prompt: {prompt}")

    return prompt


def extract_dates_to_csv_old(text):
    prompt = (
        f"I have a set of academic dates and schedules that I extracted from the internet or a PDF. "
        f"I need to identify and structure this information uniquely, avoiding duplicates. "
        f"The data includes program start/end dates and application deadlines. "
        f"Depending on the content of the extracted text, "
        f"feel free to use one or more of these columns: 'Term', 'Date', 'Session', 'Type', 'Program', or 'Description'"
        f". Each unique entry should be on a new line with elements separated by commas. "
        f"Dates should be in 'YYYY-MM-DD' format and terms like 'Fall 2023', 'Spring 2024'. "
        f"The information should be presented in a clean, organized, and unique CSV-like format. "
        f"Here is the text to process:\n'{text}'")
    logging.debug(f"Returning prompt: {prompt}")
    return prompt

def extract_tuition_to_csv(text):
    prompt = (
        f"I have extracted the following tuition details from the internet or a PDF. "
        f"These details are intended to be displayed on a study abroad agency website. The goal is to give students a "
        f"clear "
        f"understanding of the costs associated with various programs at a specific college. Your task is to convert "
        f"this information into a well-structured CSV format that clearly presents the cost for each program. "
        f"Please remember that some data fields may contain commas. Handle these cases appropriately, "
        f"consider text enclosed in quotes as a single item, even when it contains commas. "
        f"Do not preface the CSV with any additional text—only the CSV content should be returned. The tuition costs should be "
        f"prefixed with a dollar sign. Here is the obtained data: "
        f"\n'{text}'")

    logging.debug(f"Returning prompt: {prompt}")
    return prompt


def extract_requirement_to_csv(text):
    prompt = (
        f"I have extracted the following admission requirement details from the internet or a PDF. "
        f"These details are intended to be displayed on a study abroad agency website. The goal is to provide students "
        f"with a clear "
        f"understanding of the various admission requirements for different programs at specific colleges. "
        f"Your task is to convert this extracted data into a well-structured, properly formatted CSV. "
        f"Please remember that some data fields may contain commas. Handle these cases appropriately, "
        f"consider text enclosed in quotes as a single item, even when it contains commas. "
        f"Do not add or preface any additional text to the CSV — only the structured content should be returned. "
        f"Here is the obtained data:\n'{text}'")

    logging.debug(f"Returning prompt: {prompt}")
    return prompt


def choose_best_csv(csv1, csv2, csv3):
    prompt = (
        f"Below are three CSVs containing tuition details of various programs in a specific college."
        " The task is to return ONLY the number (nothing else) - 1, 2, or 3 - of the CSV that is most readable, "
        "offers clear understanding, and is best suited for display on a study abroad agency website."
        " Evaluate each CSV and return only the number of the best one."
        " Here are the CSVs:\n\n"
        "CSV 1:\n"
        f"'{csv1}'\n\n"
        "CSV 2:\n"
        f"'{csv2}'\n\n"
        "CSV 3:\n"
        f"'{csv3}'"
    )

    logging.debug(f"Returning prompt: {prompt}")
    return prompt


def gen_and_get_best_csv(prompt, text, model=None, temperature=None):
    output_texts = []
    for _ in range(3):
        while True:
            try:
                x_ = openai_prompter(
                    prompt(text),
                    model=model,
                    temperature=temperature
                )
                x = x_.lstrip("```").rstrip("```")
                x = x.replace('csv', '')
                x = x.lstrip('"').rstrip('"')
                logging.debug(f'Cleaned Response: {x}')
                x_data = StringIO(x)
                pd.read_csv(x_data, sep=',')
                logging.info(f'Good Response! Breaking...')
                output_texts.append(x)
                break
            except pd.errors.ParserError as e:
                logging.warn(f'{str(e)}, Continuing...')
                continue

    csv1, csv2, csv3 = [x for x in output_texts]

    if csv1 == csv2 == csv3:
        csv_to_return = csv1
        data = StringIO(csv_to_return)
        df = pd.read_csv(data, sep=',')
        return df

    else:

        # Initialize an empty list to store the results
        best_csv_list = []

        # Initialize result to None
        result = None

        # Run the function until we find a repeated entry or reach maximum trials
        while result is None:
            best_csv = openai_prompter(choose_best_csv(csv1, csv2, csv3), model='gpt-4', temperature=0.2)
            best_csv_list.append(best_csv)

            for item in best_csv_list:
                if best_csv_list.count(item) > 1:
                    result = item
                    break

        result = result.strip()  # Remove leading/trailing white spaces

        if result == '1':
            csv_to_return = csv1
        elif result == '2':
            csv_to_return = csv2
        elif result == '3':
            csv_to_return = csv3
        else:
            raise ValueError(f'Unexpected result: {result}')

        data = StringIO(csv_to_return)
        df = pd.read_csv(data, sep=',')
        df = df.dropna(how='all', axis=1)
        return df


def prompt_pdf_to_csv(pdf_content):
    prompt = (
        f"I have used a PDF to CSV API to extract the following CSV data. Since this data is extracted from a PDF, "
        f"it might not be in a clear or proper format. Your task is to return this information in a well-structured, "
        f"properly formatted CSV form. Feel free to modify the structure if needed, including combining or separating "
        f"columns, as long as the intended information remains clear and accessible. This information will be displayed "
        f"on a study abroad agency website, aiming to provide students with a clear understanding of the costs "
        f"associated"
        f"with various programs in a specific college. Do not preface the CSV with any additional text — only the CSV "
        f"content should be returned. Here is the obtained data: \n'{pdf_content}'")
    logging.debug(f"Returning prompt: {prompt}")
    return prompt
