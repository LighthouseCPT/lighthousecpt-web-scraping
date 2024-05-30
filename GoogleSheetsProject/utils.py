from datetime import datetime


def clear_text_and_formatting(sh, worksheet):
    requests = {
        "requests": [
            {
                "updateCells": {
                    "range": {"sheetId": worksheet._properties['sheetId']},
                    "fields": "*"
                }
            }
        ]
    }

    sh.batch_update(requests)


def next_available_row(worksheet):
    rows = worksheet.get_all_values()
    for i in range(len(rows) - 2):  # -2 to avoid index error
        # Check if current row and next 2 rows are all empty
        if all(cell == '' for cell in rows[i]) and all(cell == '' for cell in rows[i + 1]) and all(
                cell == '' for cell in rows[i + 2]):
            return i + 1
    return len(rows) + 1  # Return next row if no empty row is found

def get_latest_item(items):
    items_with_dates = [(item, datetime.strptime('_'.join(item.split('_')[-2:])[:-5], '%Y-%m-%d_%H-%M-%S'))
                        for item in items]
    latest_item = max(items_with_dates, key=lambda x: x[1])[0]
    return latest_item


for file in os.listdir('.'):
    if file.endswith('.json'):
        json_file = file
        break
else:
    raise FileNotFoundError('No .json file (credential) found.')