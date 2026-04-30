from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(slots=True)
class TeamData:
    team_name: str
    matches: Optional[pd.DataFrame] = None
    shooting: Optional[pd.DataFrame] = None
    goalkeeping: Optional[pd.DataFrame] = None
    miscellaneous: Optional[pd.DataFrame] = None
    merged_data: Optional[pd.DataFrame] = None

    def has_all_tables(self) -> bool:
        required_tables = [
            self.matches,
            self.shooting,
            self.goalkeeping,
            self.miscellaneous,
        ]
        return all(df is not None and not df.empty for df in required_tables)

    def has_merged_data(self) -> bool:
        return self.merged_data is not None and not self.merged_data.empty

    def available_tables(self) -> list[str]:
        tables = {
            "matches": self.matches,
            "shooting": self.shooting,
            "goalkeeping": self.goalkeeping,
            "miscellaneous": self.miscellaneous,
            "merged_data": self.merged_data,
        }
        return [name for name, df in tables.items() if df is not None and not df.empty]
