import os
import requests
from typing import Iterable
from dataclasses import dataclass
from datetime import date
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from time import sleep

import gspread
from gspread.models import Worksheet


CREDENTIAL_FILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
TOKEN = os.environ["GITHUB_TOKEN"]

DRIVE_SHEET_BASE_URL = "https://docs.google.com/spreadsheets/d"

REPO_INFO_QUERY = """
query ($name: String!, $owner: String!) {
  repository(name: $name, owner: $owner) {
    name
    defaultBranchRef {
      name
      target {
        ... on Commit {
          history {
            totalCount
          }
          committedDate
        }
      }
    }
    forkCount
    stargazerCount
    watchers {
      totalCount
    }
    licenseInfo {
      name
    }
    primaryLanguage {
      name
    }
    isArchived
  }
}
"""


@dataclass
class GithubRepositoryData:
    main_branch: str
    total_commits: int
    last_commit_check: bool
    fork_count: int
    stars_count: int
    watchers_count: int
    license_name: str
    primary_language: str
    is_archived: bool


@dataclass
class Github:
    gspread_row: int
    owner: str
    name: str
    data: GithubRepositoryData = None


@dataclass
class SpeadSheetTabs:
    tools: Worksheet
    github: Worksheet


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
    global CREDENTIAL_FILE, DRIVE_SHEET_BASE_URL, SHEET_ID

    gc = gspread.service_account(filename=CREDENTIAL_FILE)
    sh = gc.open_by_url(f"{DRIVE_SHEET_BASE_URL}/{SHEET_ID}")

    sheets = sh.worksheets()
    return SpeadSheetTabs(tools=sheets[0], github=sheets[1])


def fetch_data(name: str, owner: str) -> dict:
    """
    Fetch a github repository data from a given repo name and owner
    returns the query request json
    """
    global REPO_INFO_QUERY, TOKEN

    r = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "query": REPO_INFO_QUERY,
            "variables": {"name": name, "owner": owner},
        },
    )

    return r.json()


def last_commit_check(iso_date: str, months=6) -> bool:
    """
    Given a date in iso format it returns:\n
        True if date is older then months time(default 6) else False
    """
    today = date.today()
    six_months_ago = today - relativedelta(months=months)
    cur_date = isoparse(iso_date)

    return cur_date.date() < six_months_ago


def map_query_to_repository_data(api_query_data: dict) -> GithubRepositoryData:
    """
    Given an api query data it buils it into a GithubRepositoryData
    """
    repo = api_query_data["data"]["repository"]

    main_branch = repo["defaultBranchRef"]["name"]
    total_commits = repo["defaultBranchRef"]["target"]["history"]["totalCount"]
    last_commit_date = repo["defaultBranchRef"]["target"]["committedDate"]
    fork_count = repo["forkCount"]
    stars_count = repo["stargazerCount"]
    watchers_count = repo["watchers"]["totalCount"]
    license_name = repo["licenseInfo"]["name"]
    primary_language = repo["primaryLanguage"]["name"]
    is_archived = repo["isArchived"]

    return GithubRepositoryData(
        main_branch=main_branch,
        total_commits=total_commits,
        last_commit_check=last_commit_check(last_commit_date),
        fork_count=fork_count,
        stars_count=stars_count,
        watchers_count=watchers_count,
        license_name=license_name,
        primary_language=primary_language,
        is_archived=is_archived,
    )


def get_github_data(name: str, owner: str) -> GithubRepositoryData:
    """
    Fetchs a github repository and returns a GithubRepositoryData of it
    """
    data = fetch_data(name, owner)
    return map_query_to_repository_data(data)


def retrieve_repository_data(repository: Github) -> Github:
    """
    Given a Github it will fetch the github api and update it with its
    GithubRepositoryData
    """
    github_data = get_github_data(repository.name, repository.owner)
    repository.data = github_data
    return repository


def update_spreadsheet(tabs: SpeadSheetTabs, repository: Github):
    """
    Given a Github it will update the spreadsheet with its data
    """
    row = repository.gspread_row
    tabs.github.update_cell(row, 2, repository.data.stars_count)
    tabs.github.update_cell(row, 3, repository.data.fork_count)
    tabs.github.update_cell(row, 4, repository.data.total_commits)
    tabs.github.update_cell(row, 5, repository.data.last_commit_check)


if __name__ == "__main__":
    SLEEP_TIME = 2
    tabs = open_sheet()
    repositories = filter_repositories(get_github_row_url(tabs.tools))

    print("-" * 80)

    for repository in repositories:
        repository = retrieve_repository_data(repository)

        print(f"\nUpdating: {repository.owner}/{repository.name}")
        print(f"ROW: {repository.gspread_row}\n")
        update_spreadsheet(tabs, repository)
        print(f"Sleeping for {SLEEP_TIME} secongs...")
        sleep(SLEEP_TIME)
