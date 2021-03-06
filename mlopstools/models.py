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
    open_issues: int
    closed_issues: int


@dataclass
class Github:
    gspread_row: int
    use_area: str
    tool_name: str
    repo_owner: str
    repo_name: str
    repo_data: GithubRepositoryData = None


@dataclass
class SpeadSheetTabs:
    tools: Worksheet
    github: Worksheet
