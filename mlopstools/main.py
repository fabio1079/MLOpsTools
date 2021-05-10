import sys

from mlopstools.models import Github
from mlopstools.fetchers.sheetfetcher import SheetDataFetcher
from mlopstools.fetchers.githubapifetcher import GithubApiFetcher
from mlopstools.updatecsv import write_to_new_csvfile


def fetch_data() -> list[Github]:
    sheet_fetcher = SheetDataFetcher()
    repositories = sheet_fetcher.fetch()
    api_fetcher = GithubApiFetcher(repositories)

    return api_fetcher.fetch()


def update_csv(repositories: list[Github]):
    write_to_new_csvfile(repositories)
    print("done")


def update_spreadsheet(repositories: list[Github]):
    pass


def execute_update_command():
    print("Fetching data from github repositories")
    repositories = fetch_data()

    if "csv" in sys.argv:
        print("Updating CSV file")
        update_csv(repositories)

    if "sheet" in sys.argv:
        print("Updating spreadsheet")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("-" * 80)
        print("Valid commands:")
        print("-update")
        print("-u")

    if "-update" in sys.argv or "-u" in sys.argv:
        if "sheet" not in sys.argv and "csv" not in sys.argv:
            print("-" * 80)
            print("Possible actions:")
            print("\tsheet: updates google spreadsheet")
            print("\tcsv: updates csv file")
        else:
            execute_update_command()
