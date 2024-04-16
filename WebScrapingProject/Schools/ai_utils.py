from openai import OpenAI
from WebScrapingProject.log_config import configure_logger

logging = configure_logger(__name__)

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
    prompt = (f"I have a set of academic dates and schedules that I extracted from a PDF. I need to identify only the "
              f"program start and end dates, along with application deadlines (if any). This information is intended "
              f"for display on a study abroad agency website to assist prospective students. Return the output data "
              f"only in a plain CSV-like format, as 'Term, Date, Description', with each entry on a new line and "
              f"elements separated by commas. Each date should be in 'YYYY-MM-DD' format. For terms, use the full "
              f"format like 'FALL 23', 'SPRING 24' etc. Avoid any additional bibliographical conversation or content "
              f"in the response. Here is the text: \n'{text}'")
    logging.debug(f"Returning prompt: {prompt}")

    return prompt


def extract_tuition_to_csv(text):
    prompt = (f"I have extracted tuition fee details from a webpage. The information can include "
              f"program name, "
              f"tuition per credit or per term, additional applicable fees, and the estimated overall cost of "
              f"attendance. "
              f"Prepare a CSV-like output that represents these categories of information, using an appropriate format "
              f"based on the structure of the provided data. "
              f"Each entry should be listed on a new line with elements separated by commas. "
              f"Avoid any additional bibliographical "
              f"conversation or content in the response. "
              f"Here is the obtained text: \n'{text}'")
    logging.debug(f"Returning prompt: {prompt}")

    return prompt


