import json
import os
import logging
from Schools.TrineUniversity.TrineUniversity import TrineUniversityScraper

# Initialize the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SchoolScraper:
    def __init__(self):
        self.school_function_map = {
            'TrineUniversity': TrineUniversityScraper(),
        }

    def scrape_and_save(self, event):
        for school in event['schools']:
            school_name = school['name']
            info = {"tuition": school["tuition"]}
            scraper_function = self.school_function_map.get(school_name)
            if scraper_function:
                result = scraper_function.scrape(info)
                print(result)
            else:
                print({"error": f"No scraping function found for school: {school_name}"})


def lambda_handler(event, context):
    scraper = SchoolScraper()
    scraper.scrape_and_save(event)


if __name__ == "__main__":
    parent_directory = os.path.dirname(os.getcwd())
    event_path = os.path.join(parent_directory, 'events', 'event.json')
    with open(event_path, 'r') as file:
        event_data = json.load(file)
    scraper_ = SchoolScraper()
    print(scraper_.scrape_and_save(event_data))