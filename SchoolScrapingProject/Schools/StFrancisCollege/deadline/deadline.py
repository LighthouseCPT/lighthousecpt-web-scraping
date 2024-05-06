import re


def StFrancisCollege_deadline(text):
    lines = text.split('\n')
    new_lines = [re.sub('\.{3,}', '==', line) for line in lines]
    new_lines = [re.sub(r'(\d+)\s+(\d+)', r'\1\2', line) for line in new_lines]

    # Join the list elements back into a string
    new_text = '\n'.join(new_lines)

    add_ins = ["During data extraction from PDF files to CSV, identify discrepancies in academic calendar data. "
               "For instance, if a term session 'Summer B' is marked as part of first session (like '23/S1'), "
               "correct it to second session (like '23/S2'). Apply this rule consistently for other terms and "
               "sessions as well, ensuring term periods correctly align with their session labels."]

    return new_text, add_ins
