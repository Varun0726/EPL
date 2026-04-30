import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from epl_scraper import ScraperConfig, FBrefScraper
from epl_scraper.utils import DataExporter, combine_tables


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    config = ScraperConfig(
        standings_url="https://fbref.com/en/comps/9/Premier-League-Stats",
        wait_time=10,
        headless=False,
    )

    scraper = FBrefScraper(config=config)

    try:
        logger.info("Starting scraper run")
        scraper.scrape()
        logger.info("Scraped %s teams", len(scraper.team_data_list))

        exporter = DataExporter(output_dir=config.output_dir)
        exporter.export_all(scraper.team_data_list)
        logger.info("Exported individual team tables")

        combined_files = {
            "matches": "all_matches.csv",
            "shooting": "all_shooting.csv",
            "goalkeeping": "all_goalkeeping.csv",
            "miscellaneous": "all_miscellaneous.csv",
        }

        for table_attr, filename in combined_files.items():
            combined_df = combine_tables(scraper.team_data_list, table_attr)

            if combined_df.empty:
                logger.warning("No combined data available for %s", table_attr)
                continue

            output_file = config.output_dir / filename
            output_file.parent.mkdir(parents=True, exist_ok=True)
            combined_df.to_csv(output_file, index=False)
            logger.info("Saved combined file: %s", output_file)

        logger.info("Scraper run completed successfully")

    except KeyboardInterrupt:
        logger.warning("Scraper stopped manually by user")

    except Exception:
        logger.exception("Scraper failed unexpectedly")

    finally:
        scraper.close()
        logger.info("Browser closed")


if __name__ == "__main__":
    main()
