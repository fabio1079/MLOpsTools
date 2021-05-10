import requests

from typing import List
from datetime import date
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from pprint import pprint

from mlopstools.fetchers.base import BaseFetcher
from mlopstools.config import TOKEN
from mlopstools.models import Github, GithubRepositoryData


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
    openIssues: issues(states: OPEN) {
      totalCount
    }
    closedIssues: issues(states: CLOSED) {
      totalCount
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


class GithubApiFetcher(BaseFetcher):
    repositories: List[Github]

    def __init__(self, repositories: List[Github]):
        self.repositories = repositories

    def fetch(self):
        for github in self.repositories:
            self._fetch_and_update(github)

        return self.repositories

    def _query_api(self, name: str, owner: str) -> dict:
        """
        Fetch a github repository data from a given repo name and owner
        returns the query request json
        """
        print(f"Fetching {owner}/{name}")

        r = requests.post(
            "https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "query": REPO_INFO_QUERY,
                "variables": {"name": name, "owner": owner},
            },
        )

        return r.json()

    def _last_commit_check(self, iso_date: str, months=6) -> bool:
        """
        Given a date in iso format it returns:\n
            True if date is older then months time(default 6) else False
        """
        today = date.today()
        six_months_ago = today - relativedelta(months=months)
        cur_date = isoparse(iso_date)

        return cur_date.date() < six_months_ago

    def _map_query_to_repository_data(
        self, api_query_data: dict
    ) -> GithubRepositoryData:
        """
        Given an api query data it buils it into a GithubRepositoryData
        """
        repo = api_query_data["data"]["repository"]
        data = None

        try:
            main_branch = repo["defaultBranchRef"]["name"]
            total_commits = repo["defaultBranchRef"]["target"]["history"]["totalCount"]
            last_commit_date = repo["defaultBranchRef"]["target"]["committedDate"]
            fork_count = repo["forkCount"]
            stars_count = repo["stargazerCount"]
            watchers_count = repo["watchers"]["totalCount"]
            license_name = repo["licenseInfo"]["name"]
            primary_language = repo["primaryLanguage"]["name"]
            is_archived = repo["isArchived"]
            open_issues = repo["openIssues"]["totalCount"]
            closed_issues = repo["closedIssues"]["totalCount"]

            data = GithubRepositoryData(
                main_branch=main_branch,
                total_commits=total_commits,
                last_commit_check=self._last_commit_check(last_commit_date),
                fork_count=fork_count,
                stars_count=stars_count,
                watchers_count=watchers_count,
                license_name=license_name,
                primary_language=primary_language,
                is_archived=is_archived,
                open_issues=open_issues,
                closed_issues=closed_issues,
            )
        except Exception as err:
            print(err)
            pprint(repo)

        return data

    def _fetch_and_update(self, repository: Github) -> Github:
        """
        Given a Github it will fetch the github api and update it with its
        GithubRepositoryData
        """
        data = self._query_api(repository.repo_name, repository.repo_owner)
        github_data = self._map_query_to_repository_data(data)
        repository.repo_data = github_data

        return repository
