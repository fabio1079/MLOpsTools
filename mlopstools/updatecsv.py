import pathlib

from datetime import datetime

from mlopstools.models import Github


GITHUB_FIELDS = ["gspread_row", "use_area", "tool_name", "repo_owner", "repo_name"]
GITHUB_DATA_FIELDS = [
    "main_branch",
    "total_commits",
    "last_commit_check",
    "fork_count",
    "stars_count",
    "watchers_count",
    "license_name",
    "primary_language",
    "is_archived",
]


def grab_data(obj, keys: list[str]) -> list:
    data = []

    for key in keys:
        value = getattr(obj, key)

        if not isinstance(value, str):
            value = str(value)

        data.append(value)

    return data


def list_to_csvline(lst: list) -> str:
    line = ";".join(lst)
    return line + "\n"


def make_file_line_data(repository: Github) -> str:
    data = grab_data(repository, GITHUB_FIELDS)

    if repository.repo_data is not None:
        data += grab_data(repository.repo_data, GITHUB_DATA_FIELDS)

    return list_to_csvline(data)


def csv_folderpath() -> str:
    current_dir = pathlib.Path(__file__).parent.absolute()
    return f"{current_dir}/csvdata"


def write_to_new_csvfile(repositories: list[Github]):
    now = datetime.utcnow()
    filename = f"{now.date().isoformat()}.csv"

    folderpath = csv_folderpath()
    file = open(f"{folderpath}/{filename}", "w")

    print(f"Writing fetched data into {filename}")

    first_line = [*GITHUB_FIELDS, *GITHUB_DATA_FIELDS]
    file.write(list_to_csvline(first_line))

    for tool in repositories:
        if tool.repo_data is None:
            print(f"Skiping {tool.repo_owner}/{tool.repo_name} as it have not data")
            continue

        line_data = make_file_line_data(tool)
        file.write(line_data)

    file.close()
