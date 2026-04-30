import logging
import time
from typing import Optional

from seleniumbase import Driver

from .config import ScraperConfig
from .models import TeamData
from .parser import TableParser
from urllib.parse import urljoin
from .utils import merge_team_tables


class FBrefScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.driver = Driver(
            uc=True,
            headless=self.config.headless,
        )
        self.team_data_list: list[TeamData] = []

    def get_page_parser(self, url: str) -> TableParser:
        self.logger.info("Opening page: %s", url)
        self.driver.get(url)
        time.sleep(self.config.wait_time)
        html = self.driver.page_source
        return TableParser(html)

    def get_team_urls(self, parser: TableParser) -> list[str]:
        squad_links = parser.extract_team_links_from_table()

        if not squad_links:
            self.logger.warning("No squad links found on page")
            return []

        team_urls = [urljoin(self.config.base_url, link) for link in squad_links]

        self.logger.info("Found %s team URLs", len(team_urls))
        self.logger.info("Sample team URLs: %s", team_urls[:5])
        return team_urls

    def get_previous_season_url(self, parser: TableParser) -> Optional[str]:
        href = parser.get_previous_season_link()

        if not href:
            self.logger.warning("No previous season link found")
            return None

        previous_season_url = f"{self.config.base_url}{href}"
        self.logger.info("Previous season URL found: %s", previous_season_url)
        return previous_season_url

    def scrape_team(self, team_url: str) -> Optional[TeamData]:
        parser = self.get_page_parser(team_url)
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ").strip()
        self.logger.info("Scraping team: %s", team_name)

        matches = parser.read_table("Scores & Fixtures")
        if matches is None or matches.empty:
            self.logger.warning("Skipping %s: matches table missing or empty", team_name)
            return None

        shooting_links = parser.extract_links("shooting")
        goalkeeping_links = parser.extract_links("keeper")
        misc_links = parser.extract_links("misc")

        if not shooting_links:
            self.logger.warning("Skipping %s: shooting link not found", team_name)
            return None

        if not goalkeeping_links:
            self.logger.warning("Skipping %s: goalkeeping link not found", team_name)
            return None

        if not misc_links:
            self.logger.warning("Skipping %s: miscellaneous link not found", team_name)
            return None

        shooting_parser = self.get_page_parser(f"{self.config.base_url}{shooting_links[0]}")
        goalkeeping_parser = self.get_page_parser(f"{self.config.base_url}{goalkeeping_links[0]}")
        misc_parser = self.get_page_parser(f"{self.config.base_url}{misc_links[1]}")

        shooting = shooting_parser.read_table("Shooting")
        goalkeeping = goalkeeping_parser.read_table("Goalkeeping")
        miscellaneous = misc_parser.read_table("Miscellaneous")

        merged_data = None
        try:
            merged_data = merge_team_tables(
                matches=matches,
                shooting=shooting,
                goalkeeping=goalkeeping,
                miscellaneous=miscellaneous,
            )
            self.logger.info(
                "Merged team data for %s with shape %s",
                team_name,
                merged_data.shape,
            )
        except (KeyError, ValueError) as e:
            self.logger.warning("Could not merge tables for %s: %s", team_name, e)

        team_data = TeamData(
            team_name=team_name,
            matches=matches,
            shooting=shooting,
            goalkeeping=goalkeeping,
            miscellaneous=miscellaneous,
            merged_data=merged_data,
        )

        self.logger.info(
            "Finished scraping %s | available tables: %s",
            team_name,
            team_data.available_tables(),
        )
        return team_data

    def scrape(self) -> None:
        self.logger.info("Starting FBref scraper")
        parser = self.get_page_parser(self.config.standings_url)
        team_urls = self.get_team_urls(parser)

        if not team_urls:
            self.logger.warning("No team URLs found. Scraper will stop.")
            return

        for team_url in team_urls:
            try:
                team_data = self.scrape_team(team_url)
                if team_data is not None:
                    self.team_data_list.append(team_data)
            except Exception:
                self.logger.exception("Failed while scraping team URL: %s", team_url)

        self.logger.info(
            "Scraping complete | total successfully scraped teams: %s",
            len(self.team_data_list),
        )

    def close(self) -> None:
        if hasattr(self, "driver") and self.driver:
            self.logger.info("Closing browser")
            self.driver.quit()
