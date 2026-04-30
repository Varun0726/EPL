import logging
from io import StringIO
from typing import List, Optional

import pandas as pd
from bs4 import BeautifulSoup


class TableParser:
    def __init__(self, html: str):
        self.html = html
        self.cleaned_html = html.replace("<!--", "").replace("-->", "")
        self.soup = BeautifulSoup(self.cleaned_html, "html.parser")
        self.logger = logging.getLogger(__name__)

    def safe_select_one(self, selector: str):
        element = self.soup.select_one(selector)
        if element is None:
            self.logger.warning("No element found for selector: %s", selector)
            return None
        return element

    def extract_links(self, keyword: str) -> List[str]:
        links = [a.get("href") for a in self.soup.find_all("a", href=True)]
        filtered_links = [link for link in links if link and keyword in link]
        self.logger.info("Found %s links for keyword '%s'", len(filtered_links), keyword)
        return filtered_links

    def extract_team_links_from_table(self, selector: str = "table.stats_table") -> List[str]:
        table = self.safe_select_one(selector)
        if table is None:
            return []

        links = [a.get("href") for a in table.find_all("a", href=True)]

        squad_links = [
            link for link in links
            if link
            and link.startswith("/en/squads/")
            and link.endswith("-Stats")
            and "all_comps" not in link
            and "matchlogs" not in link
            and "/shooting/" not in link
            and "/keeper/" not in link
            and "/misc/" not in link
        ]

        unique_links = list(dict.fromkeys(squad_links))
        self.logger.info("Found %s filtered squad links in standings table", len(unique_links))
        return unique_links

    def read_table(self, match_text: str) -> Optional[pd.DataFrame]:
        try:
            tables = pd.read_html(StringIO(self.cleaned_html), match=match_text)
            if not tables:
                self.logger.warning("No table matched: %s", match_text)
                return None

            df = tables[0]

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel()

            self.logger.info("Successfully read table: %s", match_text)
            return df

        except ValueError:
            self.logger.warning("read_html failed for table match: %s", match_text)
            return None

    def get_previous_season_link(self) -> Optional[str]:
        prev_link = self.safe_select_one("a.prev")
        if not prev_link:
            return None

        href = prev_link.get("href")
        if not href:
            self.logger.warning("Previous season link found, but href is missing")
            return None

        return href

    def get_page_title(self) -> Optional[str]:
        if self.soup.title and self.soup.title.string:
            return self.soup.title.string.strip()
        return None
