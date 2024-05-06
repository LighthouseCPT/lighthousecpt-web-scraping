from log_config import configure_logger

logger = configure_logger(__name__)


def extract_deadline_to_csv(text, add_ins, programs):
    if add_ins is not None:
        add_ins = ', '.join(add_ins)

    prompt = (
        f"We have extracted academic dates and schedules from a source. "
        f"We need to format this information into a structured CSV format suitable for prospective students interested "
        f"in the '{programs}' program. "
        f"Please discard any undergraduate information. If any information applies to both undergraduate and graduate "
        f"students, include it but rename it as graduate information."
        f"The goal is to ONLY identify the program/class start and end dates, "
        f"as well as application deadlines (if any). "
        f"Depending on the content, you may need to use the following columns: 'Term', 'Date', 'Session', and 'Type'. "
        f"Maintain this column order in the CSV. "
        f"If the dates are given in ranges, for instance, '2024-05-20 - 2024-07-14', split them into two separate "
        f"rows: one for 'Start Date' and one for 'End Date'. If a data item includes commas, enclose it in quotes."
        f"Ensure all dates are in 'YYYY-MM-DD' format. Terms should be expressed fully, like 'Fall 2023' or 'Spring "
        f"2023'. If a term is presented as 'Spring II: April 1, 2024', it represents 'Term' as 'Spring 2024', "
        f"'Session' as '2', 'Date' as '2024-04-01', and 'Type' could be deadline, start date, end date, etc."
        f"If it just says for example 'Summer 2024 Term', then that means the 'Session' is '1'. "
        f"If it says for example 'Spring 2025 Full Session', then that means the 'Session' is 'Full'. "
        f"Additional instructions for this specific data extraction are as follows: {add_ins}."
        f"Avoid any additional bibliographical conversation or content in the response. "
        f"CRITICAL: Only return back the CSV. "
        f"The data for conversion is:\n'{text}'."
    )

    logger.debug(f"Returning prompt: {prompt}")
    return prompt


def extract_tuition_to_csv(text, add_ins, programs):
    if add_ins is not None:
        add_ins = ', '.join(add_ins)

    prompt = (
        f"We have extracted tuition details from a source. "
        f"We need to format this information into a structured CSV format suitable for prospective students interested "
        f"in the '{programs}' program. "
        f"Discard any undergraduate information. If any information applies to both undergraduate and graduate "
        f"students, include it but rename it as graduate information."
        f"We need to ONLY identify costs directly related to the program/class, such as tuition costs, "
        f"admission costs, registration fees, application fees and administrative fees. "
        f"Do not include unrelated costs such as student ID card fee, returned check fee, CPA Becker Review fees, "
        f"Instructional Resource Fee, Foundation Classes, personal expenses, off-campus costs, or "
        f"any unspecified estimated fees. "
        f"If all programs share the same fees, just record them once with 'All Programs' in the 'Program' column. "
        f"'Estimated fees' and 'Fees' should not be included unless they're specified as admission-related fees. "
        f"Use the following columns depending on the content: 'Program', 'Total Units', 'Type', and "
        f"'Cost'. Be sure to keep this column order in the CSV. "
        f"Full program names should be noted in the 'Program' column, with any abbreviations shown in brackets "
        f"like 'Full Program Name (Short Form)'. "
        f"Each cost in the 'Cost' column should begin with a dollar sign, "
        f"presented without commas regardless of the number's size."
        f"If a data item has commas, enclose it in quotes."
        f"Additional instructions for this specific data extraction are as follows: {add_ins}."
        f"Avoid any additional contextual conversation or content in the response. "
        f"CRITICAL: Return only the CSV. "
        f"The data for conversion is:\n'{text}'."
    )

    logger.debug(f"Returning prompt: {prompt}")
    return prompt


def extract_requirement_to_csv(text, add_ins, programs):
    if add_ins is not None:
        add_ins = ', '.join(add_ins)
    prompt = (
        f"We have extracted the following admission requirement details from a source. "
        f"Our goal is to provide clear requirement insights for prospective students interested in '{programs}'. "
        f"Please format the extracted information pertaining to these programs into a structured CSV format. "
        f"The structured content should provide prospective students with a clear understanding of the various "
        f"admission requirements for these programs. "
        f"If a data item has commas, enclose it in quotes."
        f"Additional instructions for this specific data extraction are as follows: {add_ins}."
        f"Avoid any additional contextual conversation or content in the response. "
        f"CRITICAL: Return only the CSV. "
        f"The data for conversion is:\n'{text}'."
    )

    logger.debug(f"Returning prompt: {prompt}")
    return prompt
