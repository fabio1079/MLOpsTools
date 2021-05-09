import sys

from mlopstools.models import Github
from mlopstools.sheet import grab_github_repositories
from mlopstools.collectdata import update_github_with_data
from mlopstools.updatecsv import write_to_new_csvfile


def fetch_data() -> list[Github]:
    repositories = grab_github_repositories()
    repositories = update_github_with_data(repositories)
    return repositories


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
