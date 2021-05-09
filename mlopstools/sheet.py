from typing import Iterable

import gspread
from gspread.models import Worksheet

from mlopstools.config import CREDENTIAL_FILE, DRIVE_SHEET_BASE_URL, SHEET_ID
from mlopstools.models import Github, SpeadSheetTabs


def get_github_row_url(sheet: Worksheet) -> Iterable[tuple[int, str]]:
    """
    Given the tools Worksheet it returns an iterable of tuples
    (row number, github url)
    """
    github_urls = sheet.col_values(3)
    row_and_url = enumerate(github_urls[1:], start=2)

    return ((i, url) for i, url in row_and_url)


def filter_repositories(rows: Iterable[tuple[int, str]]) -> Iterable[Github]:
    """
    Given an iterable of (row number, github url) it returns an iterable of
    Github
    """
    github_data = []

    for row, url in rows:
        parts = url.split("/")

        if len(parts) < 5:
            print(f"Not a repository: {url}")
            continue

        owner = parts[3]
        name = parts[4]

        github = Github(gspread_row=row, owner=owner, name=name)
        github_data.append(github)

    return github_data


def open_sheet() -> SpeadSheetTabs:
    """
    Open a google drive spreadsheet and returns a list of Worksheet
    """
    gc = gspread.service_account(filename=CREDENTIAL_FILE)
    sh = gc.open_by_url(f"{DRIVE_SHEET_BASE_URL}/{SHEET_ID}")

    sheets = sh.worksheets()
    return SpeadSheetTabs(tools=sheets[0], github=sheets[1])


def grab_github_repositories() -> Iterable[Github]:
    """
    Access google spreadsheet and gets the github repositories urls and then
    build a list of Github
    """
    tabs = open_sheet()
    return filter_repositories(get_github_row_url(tabs.tools))
