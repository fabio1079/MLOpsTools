import pathlib
from datetime import datetime
from dataclasses import fields
from typing import List

from mlopstools.updaters.baseupdater import BaseUpdater
from mlopstools.models import Github, GithubRepositoryData

GITHUB_FIELDS = [field.name for field in fields(Github)]
GITHUB_FIELDS.remove("repo_data")

GITHUB_DATA_FIELDS = [field.name for field in fields(GithubRepositoryData)]


class CSVFileGenerator(BaseUpdater):
    repositories: List[Github]

    def __init__(self, repositories: List[Github]):
        self.repositories = repositories

    def update(self):
        filename, file = self._create_csv_file()

        print(f"Writing fetched data into {filename}")

        first_line = [*GITHUB_FIELDS, *GITHUB_DATA_FIELDS]
        file.write(self._list_to_csvline(first_line))

        for tool in self.repositories:
            if tool.repo_data is None:
                print(f"Skiping {tool.repo_owner}/{tool.repo_name} as it have not data")
                continue

            line_data = self._make_file_line_data(tool)
            file.write(line_data)

        file.close()

    def _csv_folderpath(self) -> str:
        current_dir = pathlib.Path(__file__).parent.absolute()
        return f"{current_dir}/../csvdata"

    def _create_csv_file(self):
        now = datetime.utcnow()
        filename = f"{now.date().isoformat()}.csv"

        folderpath = self._csv_folderpath()
        file = open(f"{folderpath}/{filename}", "w")

        return filename, file

    def _grab_data(self, obj, keys: List[str]) -> List[str]:
        data = []

        for key in keys:
            value = getattr(obj, key)

            if not isinstance(value, str):
                value = str(value)

            data.append(value)

        return data

    def _list_to_csvline(self, lst: List[str]) -> str:
        line = ";".join(lst)
        return line + "\n"

    def _make_file_line_data(self, repository: Github) -> str:
        data = self._grab_data(repository, GITHUB_FIELDS)

        if repository.repo_data is not None:
            data += self._grab_data(repository.repo_data, GITHUB_DATA_FIELDS)

        return self._list_to_csvline(data)
