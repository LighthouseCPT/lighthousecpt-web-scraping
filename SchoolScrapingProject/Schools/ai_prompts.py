from log_config import configure_logger
logging = configure_logger(__name__)


# def extract_dates_to_csv_old(text):
#     prompt = (
#         f"I have a set of academic dates and schedules that I extracted from the internet or a PDF. "
#         f"I need to identify and structure this information uniquely, avoiding duplicates. "
#         f"The data includes program start/end dates and application deadlines. "
#         f"Depending on the content of the extracted text, "
#         f"feel free to use one or more of these columns: 'Term', 'Date', 'Session', 'Type', 'Program', or 'Description'"
#         f". Each unique entry should be on a new line with elements separated by commas. "
#         f"Dates should be in 'YYYY-MM-DD' format and terms like 'Fall 2023', 'Spring 2024'. "
#         f"The information should be presented in a clean, organized, and unique CSV-like format. "
#         f"Here is the text to process:\n'{text}'")
#     logging.debug(f"Returning prompt: {prompt}")
#     return prompt


def extract_tuition_to_csv_old(text):
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


def extract_tuition_to_csv(text, programs):
    prompt = (
        f"We have extracted the following tuition details from a source. "
        f"Our goal is to present clear cost insights for prospective students interested in '{programs}'. "
        f"Please format the extracted information pertaining to these specified programs into a structured CSV format. "
        f"Include full program names in the 'Program' column, with any short form represented in brackets like 'Full "
        f"Program Name (Short Form)', and ensure to fill out 'Total Units', 'Type', 'Cost' "
        f"columns based on the available data. "
        f"Do not include 'estimated fees' as they often lack clarity, unless they're specified as admission-related. "
        f"Extract only the direct costs related to the programs and general costs that apply to all students. "
        f"Exclude personal expenses, off-campus costs, unclarified estimated fees or unrelated expenditures. "
        f"All costs in the 'Cost' column should be prefixed with a dollar sign. "
        f"If a data item in the text contains commas, enclose that item in quotes when entering into the CSV format. "
        f"The goal is to create a CSV with only relevant cost data, formatted correctly for ease of analysis. "
        f"No additional textual information should be included in the CSV. "
        f"Here's the data that needs to be converted:\n'{text}'")

    logging.debug(f"Returning prompt: {prompt}")
    return prompt


def extract_tuition_to_csv_old2(text, programs):
    prompt = (
        f"We have extracted the following tuition details from a webpage or a PDF. "
        f"Our objective is to provide clear cost insights for prospective students interested in the "
        f"'{programs}' program. Make sure to return the full program names in the 'Program' column, and only include "
        f"information pertaining to these specified programs. "
        f"Depending on the content of the extracted text feel free to use one or more "
        f"of these columns: 'Program', 'Total Units', 'Type', 'Cost'. "
        f"Please exclude any columns or rows related to 'estimated fees' as they can be vague and unclear, "
        f"unless it clearly specifies that the fees are admission-related. "
        f"Your task is to extract the direct costs related to this program and general costs applicable to all "
        f"students of these specified programs, excluding any personal, off-campus, unclarified estimated fees or "
        f"unrelated expenses. Then, convert this information into a "
        f"structured CSV format. Remember, the CSV should only contain the relevant cost data "
        f"with no additional text. All costs should be prefixed with a dollar sign. Also, handle data fields with "
        f"commas appropriately. If text is enclosed in quotes, consider it as a single item, even if it contains "
        f"commas. Here is the collected data:\n'{text}'")

    logging.debug(f"Returning prompt: {prompt}")
    return prompt


def extract_dates_to_csv(text, programs):
    prompt = (
        f"We have extracted the following academic dates and schedules from a source. "
        f"Our goal is to present clear date insights for prospective students interested in the '{programs}' program. "
        f"Please format the extracted information pertaining specifically to these programs into a structured CSV format. "
        f"We need to identify the program start and end dates, along with application deadlines (if any). "
        f"Depending on the content of the extracted text, feel free to use one or more of these columns: "
        f"'Term', 'Date', 'Session', 'Type', 'Program', or 'Description'. "
        f"Each unique entry should be on a new line with elements separated by commas. "
        f"Handle data fields with commas appropriately - consider text enclosed in quotes as a single item. "
        f"Each date should be in 'YYYY-MM-DD' format and terms should be in the full format like 'Fall 2023', "
        f"'Spring 2024', etc. "
        f"Avoid any additional bibliographical conversation or content in the response. "
        f"Here's the data that needs to be converted:\n'{text}'")

    logging.debug(f"Returning prompt: {prompt}")
    return prompt


def extract_requirement_to_csv(text, programs):
    prompt = (
        f"We have extracted the following admission requirement details from a source. "
        f"Our goal is to provide clear requirement insights for prospective students interested in '{programs}'. "
        f"Please format the extracted information pertaining to these programs into a structured CSV format. "
        f"The structured content should provide prospective students with a clear understanding of the various "
        f"admission requirements for these programs. "
        f"Handle data fields with commas appropriately and consider text enclosed in quotes as a single item, even "
        f"when it contains commas. "
        f"Do not add or preface any additional text to the CSV — its goal is to provide only relevant requirement data, "
        f"formatted correctly for ease of understanding. "
        f"Here's the data that needs to be converted:\n'{text}'")

    logging.debug(f"Returning prompt: {prompt}")
    return prompt

# def prompt_pdf_to_csv(pdf_content):
#     prompt = (
#         f"I have used a PDF to CSV API to extract the following CSV data. Since this data is extracted from a PDF, "
#         f"it might not be in a clear or proper format. Your task is to return this information in a well-structured, "
#         f"properly formatted CSV form. Feel free to modify the structure if needed, including combining or separating "
#         f"columns, as long as the intended information remains clear and accessible. This information will be displayed "
#         f"on a study abroad agency website, aiming to provide students with a clear understanding of the costs "
#         f"associated"
#         f"with various programs in a specific college. Do not preface the CSV with any additional text — only the CSV "
#         f"content should be returned. Here is the obtained data: \n'{pdf_content}'")
#     logging.debug(f"Returning prompt: {prompt}")
#     return prompt
