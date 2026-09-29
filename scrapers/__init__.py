from .workday import check_workday
from .amazon import check_amazon
from .microsoft import check_microsoft
from .google import check_google

SCRAPERS = {
    "workday": lambda cfg, start_date, valid_relative: check_workday(cfg, valid_relative),
    "amazon": lambda cfg, start_date, valid_relative: check_amazon(cfg, start_date),
    "microsoft": lambda cfg, start_date, valid_relative: check_microsoft(cfg, start_date),
    "google": lambda cfg, start_date, valid_relative: check_google(cfg, start_date),
}

def scrape_company(config, start_date, valid_relative):
    scraper_type = config.get("type", "").lower()
    scraper_fn = SCRAPERS.get(scraper_type)
    if not scraper_fn:
        print(f"[{config.get('name', 'Unknown')}] Unknown scraper type: '{scraper_type}'")
        return []
    return scraper_fn(config, start_date, valid_relative)
