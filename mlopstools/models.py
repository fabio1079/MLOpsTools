from dataclasses import dataclass

from gspread.models import Worksheet


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
