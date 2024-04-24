import re


def StFrancisCollege_deadline(text):
    lines = text.split('\n')
    new_lines = [re.sub('\.{3,}', '==', line) for line in lines]
    new_lines = [re.sub(r'(\d+)\s+(\d+)', r'\1\2', line) for line in new_lines]

    # Join the list elements back into a string
    new_text = '\n'.join(new_lines)

    return new_text
