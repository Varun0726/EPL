from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd

from .models import TeamData


logger = logging.getLogger(__name__)


class DataExporter:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_dataframe(self, df: pd.DataFrame, file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False)
        logger.info("Saved file: %s", file_path)

    def save_team_tables(self, team_data: TeamData) -> None:
        safe_team_name = team_data.team_name.lower().replace(" ", "_")

        table_mapping = {
            "matches": team_data.matches,
            "shooting": team_data.shooting,
            "goalkeeping": team_data.goalkeeping,
            "miscellaneous": team_data.miscellaneous,
            "merged_data": team_data.merged_data,
        }

        for table_name, df in table_mapping.items():
            if df is not None and not df.empty:
                file_path = self.output_dir / f"{safe_team_name}_{table_name}.csv"
                self.save_dataframe(df, file_path)
            else:
                logger.warning(
                    "Skipped saving %s for %s because the table is missing or empty",
                    table_name,
                    team_data.team_name,
                )

    def export_all(self, team_data_list: Iterable[TeamData]) -> None:
        for team_data in team_data_list:
            self.save_team_tables(team_data)


def combine_tables(team_data_list: Iterable[TeamData], table_attr: str) -> pd.DataFrame:
    valid_attrs = {"matches", "shooting", "goalkeeping", "miscellaneous", "merged_data"}
    if table_attr not in valid_attrs:
        raise ValueError(f"Invalid table_attr '{table_attr}'. Must be one of {valid_attrs}.")

    frames: list[pd.DataFrame] = []

    for team_data in team_data_list:
        df = getattr(team_data, table_attr, None)

        if df is not None and not df.empty:
            temp_df = df.copy()
            temp_df["team_name"] = team_data.team_name
            frames.append(temp_df)

    if not frames:
        logger.warning("No valid DataFrames found for table_attr='%s'", table_attr)
        return pd.DataFrame()

    combined_df = pd.concat(frames, ignore_index=True)
    logger.info("Combined %s tables into one DataFrame with shape %s", table_attr, combined_df.shape)
    return combined_df


def merge_team_tables(
    matches: pd.DataFrame,
    shooting: pd.DataFrame,
    goalkeeping: pd.DataFrame,
    miscellaneous: pd.DataFrame,
) -> pd.DataFrame:
    required_frames = {
        "matches": matches,
        "shooting": shooting,
        "goalkeeping": goalkeeping,
        "miscellaneous": miscellaneous,
    }

    for name, df in required_frames.items():
        if df is None or df.empty:
            raise ValueError(f"{name} DataFrame is missing or empty")
        if "Date" not in df.columns:
            raise KeyError(f"'Date' column missing from {name} DataFrame")

    matches_df = matches.copy()
    shooting_df = shooting.copy()
    goalkeeping_df = goalkeeping.copy()
    misc_df = miscellaneous.copy()

    for df in [matches_df, shooting_df, goalkeeping_df, misc_df]:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    shooting_keep = ["Date", "Sh", "SoT", "PK", "PKatt", "Gls", "SoT%", "G/Sh", "G/SoT"]
    goalkeeping_keep = ["Date", "SoTA", "GA", "Saves", "Save%", "CS", "PKatt", "PKA", "PKsv", "PKm"]
    misc_keep = ["Date", "CrdY", "CrdR", "2CrdY", "Fls", "Fld", "Off", "Crs", "Int", "TklW", "PKwon", "PKcon", "OG"]

    missing_shooting = [col for col in shooting_keep if col not in shooting_df.columns]
    missing_goalkeeping = [col for col in goalkeeping_keep if col not in goalkeeping_df.columns]
    missing_misc = [col for col in misc_keep if col not in misc_df.columns]

    if missing_shooting:
        raise KeyError(f"Missing shooting columns: {missing_shooting}")
    if missing_goalkeeping:
        raise KeyError(f"Missing goalkeeping columns: {missing_goalkeeping}")
    if missing_misc:
        raise KeyError(f"Missing miscellaneous columns: {missing_misc}")

    shooting_df = shooting_df[shooting_keep].copy().rename(
        columns={"PKatt": "PKatt_shooting"}
    )
    goalkeeping_df = goalkeeping_df[goalkeeping_keep].copy().rename(
        columns={"PKatt": "PKatt_goalkeeping"}
    )
    misc_df = misc_df[misc_keep].copy()

    team_data = matches_df.merge(shooting_df, on="Date", how="left")
    team_data = team_data.merge(goalkeeping_df, on="Date", how="left")
    team_data = team_data.merge(misc_df, on="Date", how="left")

    return team_data.sort_values("Date").reset_index(drop=True)
