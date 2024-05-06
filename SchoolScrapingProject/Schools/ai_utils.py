import os
from io import StringIO
import pandas as pd
from openai import OpenAI
from Schools.utils import drop_duplicate_columns, convert_csv_to_df
from log_config import configure_logger

logger = configure_logger(__name__)


def openai_prompter(prompt, model=None, temperature=None):
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": f"{prompt}"}
            ],
            temperature=temperature
        )
        response = completion.choices[0].message.content
        msg = f"Successfully generated response: {response}"
        logger.debug(msg)
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Unable to generate response: {str(e)}")


def choose_best_csv(used_prompt, csv1, csv2, csv3):
    prompt = (
        f"Here is the prompt I used:\n\n'{used_prompt}'\n\nUsing it, I obtained three CSVs. "
        "The task is to return ONLY the number (nothing else) - 1, 2, or 3 - of the CSV that adhered most closely to "
        "the prompt. Evaluate each CSV and return only the number of the one that best follows this prompt. "
        "Here are the CSVs:\n\n"
        "CSV 1:\n"
        f"'{csv1}'\n\n"
        "CSV 2:\n"
        f"'{csv2}'\n\n"
        "CSV 3:\n"
        f"'{csv3}'"
    )

    logger.debug(f"Returning prompt: {prompt}")
    return prompt


def gen_and_get_best_csv(prompt, text, add_ins, programs, model=None, temperature=None):
    output_texts = []
    for _ in range(3):
        while True:
            try:
                x_ = openai_prompter(
                    prompt(text, add_ins, programs),
                    model=model,
                    temperature=temperature
                )
                x = x_.replace("```", "")
                x = x.replace('csv', '')
                logger.info(f'Cleaned Response: {x}')
                x_data = StringIO(x)
                pd.read_csv(x_data, sep=',')
                logger.info(f'Good Response! Breaking...')
                output_texts.append(x)
                break
            except pd.errors.ParserError as e:
                logger.warn(f'{str(e)}, Continuing...')
                continue

    csv1, csv2, csv3 = [x for x in output_texts]

    if csv1 == csv2 == csv3:
        _ = None
        df = convert_csv_to_df(csv1)
        return df, _, _

    else:

        best_csv_list = []

        result = None
        while result is None:
            best_csv = openai_prompter(choose_best_csv(prompt(text, add_ins, programs), csv1, csv2, csv3), model='gpt-4',
                                       temperature=0.2)
            best_csv_list.append(best_csv)

            for item in best_csv_list:
                if best_csv_list.count(item) > 1:
                    result = item
                    break

        result = result.strip()

        csv_dict = {'1': csv1, '2': csv2, '3': csv3}

        if result not in csv_dict:
            raise ValueError(f'Unexpected result: {result}')

        df1 = convert_csv_to_df(csv_dict[result])

        remaining_csvs = [csv for key, csv in csv_dict.items() if key != result]

        df2 = convert_csv_to_df(remaining_csvs[0])
        df3 = convert_csv_to_df(remaining_csvs[1])

        df1 = drop_duplicate_columns(df1)
        df2 = drop_duplicate_columns(df2)
        df3 = drop_duplicate_columns(df3)

        return df1, df2, df3

