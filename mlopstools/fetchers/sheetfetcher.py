from typing import Iterable, Tuple

import gspread
from gspread.models import Worksheet, Spreadsheet

from mlopstools.config import CREDENTIAL_FILE, DRIVE_SHEET_BASE_URL, SHEET_ID
from mlopstools.models import Github, SpeadSheetTabs
from mlopstools.fetchers.base import BaseFetcher


class SheetDataFetcher(BaseFetcher):
    sheet: SpeadSheetTabs

    def __init__(self):
        self.sheet = self._open_sheet()

    def fetch(self) -> Iterable[Github]:
        areas = self._get_col_data(self.sheet.tools, 1)
        names = self._get_col_data(self.sheet.tools, 2)
        urls = self._get_col_data(self.sheet.tools, 3)

        return self._build_github_list(areas, names, urls)

    def _open_sheet(self) -> SpeadSheetTabs:
        """
        Open a google drive spreadsheet and returns a list of Worksheet
        """
        gc = gspread.service_account(filename=CREDENTIAL_FILE)
        sh = gc.open_by_url(f"{DRIVE_SHEET_BASE_URL}/{SHEET_ID}")

        sheets = sh.worksheets()
        return SpeadSheetTabs(tools=sheets[0], github=sheets[1])

    def _get_col_data(self, sheet: Worksheet, col_number: int) -> list:
        data = sheet.col_values(col_number)
        return data[1:]  # Skip first line as it is the column name

    def _get_repository_from_url(self, url: str) -> Tuple[str, str]:
        parts = url.split("/")

        if len(parts) != 5:
            raise Exception(f"Not a repository: {url}")

        owner = parts[3]
        name = parts[4]

        return (owner, name)

    def _build_github_list(
        self, areas: list, names: list, urls: list
    ) -> Iterable[Github]:
        gspread_row = 1

        hubs = []
        for (use_area, tool_name, url) in zip(areas, names, urls):
            gspread_row += 1

            try:
                (owner, name) = self._get_repository_from_url(url)

                github = Github(
                    gspread_row=gspread_row,
                    use_area=use_area,
                    tool_name=tool_name,
                    repo_owner=owner,
                    repo_name=name,
                )

                hubs.append(github)
            except Exception as e:
                print(e)

        return hubs
