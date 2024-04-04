import importlib


class SchoolScraper:
    def __init__(self, SOURCE_BUCKET, CSV_BUCKET, school_name, info):
        moduleBasePath = f"Schools.{school_name}"

        self.school_name = school_name

        if info.get("tuition") != "NOT_REQUIRED":
            TuitionScraperModule = importlib.import_module(f"{moduleBasePath}.Tuition.Tuition")
            self.tuition_scraper = getattr(TuitionScraperModule, "TuitionScraper")(SOURCE_BUCKET, CSV_BUCKET,
                                                                                   school_name)
        else:
            self.tuition_scraper = None

        if info.get("requirement") != "NOT_REQUIRED":
            RequirementScraperModule = importlib.import_module(f"{moduleBasePath}.Requirement.Requirement")
            self.requirement_scraper = getattr(RequirementScraperModule, "RequirementScraper")(SOURCE_BUCKET,
                                                                                               CSV_BUCKET,
                                                                                               school_name)
        else:
            self.requirement_scraper = None

        if info.get("deadline") != "NOT_REQUIRED":
            DeadlineScraperModule = importlib.import_module(f"{moduleBasePath}.Deadline.Deadline")
            self.deadline_scraper = getattr(DeadlineScraperModule, "DeadlineScraper")(SOURCE_BUCKET, CSV_BUCKET,
                                                                                      school_name)
        else:
            self.deadline_scraper = None

    def scrape(self, info):
        print(info)
        tuition_url = info.get("tuition")
        requirement_url = info.get("requirement")
        deadline_url = info.get("deadline")

        if tuition_url and tuition_url != "NOT_REQUIRED":
            self.tuition_scraper.scrape(tuition_url)
        if requirement_url and requirement_url != "NOT_REQUIRED":
            self.requirement_scraper.scrape(requirement_url)
        if deadline_url and deadline_url != "NOT_REQUIRED":
            self.deadline_scraper.scrape(deadline_url)
