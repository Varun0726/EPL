from dataclasses import dataclass, field
from pathlib import Path


@dataclass(kw_only=True, slots=True, frozen=True)
class ScraperConfig:
    standings_url: str = "https://fbref.com/en/comps/9/Premier-League-Stats"
    base_url: str = "https://fbref.com"
    wait_time: int = 3
    headless: bool = False
    output_dir: Path = field(default_factory=lambda: Path("data"))

    def __post_init__(self):
        if self.wait_time < 0:
            raise ValueError("wait_time must be 0 or greater")

        if not self.standings_url.startswith("http"):
            raise ValueError("standings_url must be a valid absolute URL")

        if not self.base_url.startswith("http"):
            raise ValueError("base_url must be a valid absolute URL")
