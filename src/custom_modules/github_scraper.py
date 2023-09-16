from datetime import datetime, timedelta
from urllib.parse import urlparse
from requests import get
from os import environ


class GitHubRepoUrlError(Exception):
    """
    Exception raised when a GitHub repository URL is invalid
    """

    def __init__(self, repo_url: str, *args: object) -> None:
        super().__init__(*args)
        self.repo_url = repo_url

    # Override the __str__ method to print custom message
    def __str__(self) -> str:
        return f'"{self.repo_url}" is not a valid GitHub repository URL'


def export_github_access_token_to_env_var(github_token: str):
    """
    Export the GitHub access token to an environment variable called `GITHUB_TOKEN`
    """
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = "https://api.github.com/user"
    response = get(url, headers=headers)
    if response.status_code == 200:
        environ["GITHUB_TOKEN"] = github_token
        return "Correctly authenticated your github token"
    else:
        return "Incorrect github token"

    # environ['GITHUB_TOKEN'] = github_token


def _build_repo_url_for_api_calls(repo_url: str) -> str:
    """
    Build the URL to be used for API calls to the GitHub API, and validate the URL provided as well.

    The specific endpoint to be used from the api should still be appended to the returned URL. (e.g. /pulls, /issues, etc.)
    """
    # Parse the URL and extract the path
    parsed_url = urlparse(repo_url)

    # Check if the host is GitHub
    if parsed_url.hostname != "github.com":
        raise GitHubRepoUrlError(repo_url)

    # Check if the path has the right number of components
    path = parsed_url.path
    path_components = path.split("/")

    if len(path_components) < 3:
        raise GitHubRepoUrlError(repo_url)

    repo_owner = path_components[1]
    repo_name = path_components[2]
    if repo_owner == "" or repo_name == "":
        raise GitHubRepoUrlError(repo_url)

    url_for_api_calls = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    return url_for_api_calls


def _filter_pr_event_dict(pr_event: dict) -> dict:
    """
    Filters only the needed keys from the pull request event dictionary
    """
    needed_keys = ["number", "title", "body", "merged_at"]
    filtered_pr_event = {k: pr_event[k] for k in needed_keys}
    if filtered_pr_event["merged_at"] is not None:
        merged_at_str: str = filtered_pr_event["merged_at"]
        merged_at_str_iso = merged_at_str.replace("Z", "")
        filtered_pr_event["merged_at"] = datetime.fromisoformat(merged_at_str_iso)
    return filtered_pr_event


def _filter_pr_review_dict(pr_review: list) -> dict:
    username = pr_review["user"]["login"]
    state = pr_review["state"]
    submitted_at_str: str = pr_review["submitted_at"]
    submitted_at_str_iso = submitted_at_str.replace("Z", "")
    submitted_at = datetime.fromisoformat(submitted_at_str_iso)

    filterd_pr_review = {
        "username": username,
        "state": state,
        "submitted_at": submitted_at,
    }

    return filterd_pr_review


def _get_pr_reviews(pr_data_endpoint_url: str, pr_number: int, request_headers: dict):
    # NOTE: this function assumes that the max number of reviews per pull request is 100 (which is already absurdly high)

    pr_reviews_endpoint_url = f"{pr_data_endpoint_url}/{pr_number}/reviews"

    query_params = {"per_page": 100, "page": 1}

    response = get(
        pr_reviews_endpoint_url, headers=request_headers, params=query_params
    )
    raw_pr_reviews = response.json()
    filtered_pr_reviews = [
        _filter_pr_review_dict(pr_review) for pr_review in raw_pr_reviews
    ]
    return filtered_pr_reviews


def get_github_repo_pull_requests_filterd_data(repo_url: str, days_back: int):
    """
    Iteratively get all the pull requests for a given repository, only the ones that were merged in the last `days_back` days.

    ## Parameters:
    - `repo_url`: The URL of the repository to get the pull requests for.
    - `days_back`: The number of days to go back in time to get the pull requests for.
    - `github_token`: The GitHub API token to be used for authentication.

    ## Returns:
    A list of dictionaries, each dictionary represents a pull request.
    """
    try:
        GITHUB_TOKEN = environ["GITHUB_TOKEN"]
    except KeyError:
        raise KeyError(
            "The GitHub API token is not set. Please set it using `export_github_access_token_to_env_var`"
        )
    earliest_pr_merge_date = datetime.now() - timedelta(days=days_back)

    repo_api_url = _build_repo_url_for_api_calls(repo_url)
    pr_data_endpoint_url = f"{repo_api_url}/pulls"

    request_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    query_params = {
        "state": "closed",  # NOTE: This should be changed to "all" if we want to get all the pull requests, not just the closed ones
        "per_page": 100,
        "page": 1,  # this will be used to paginate the results (to be updated in the loop below)
    }

    filtered_pr_events = []
    while True:
        response = get(
            pr_data_endpoint_url, headers=request_headers, params=query_params
        )
        raw_pr_events = response.json()

        # check if the response is empty (we have already paginated through all the results)
        if len(raw_pr_events) == 0:
            break

        else:
            for raw_pr_event in raw_pr_events:
                filtered_pr_event = _filter_pr_event_dict(raw_pr_event)
                merged_at = filtered_pr_event["merged_at"]
                if merged_at is not None and merged_at < earliest_pr_merge_date:
                    break
                else:
                    pr_raw_reviews = _get_pr_reviews(
                        pr_data_endpoint_url,
                        filtered_pr_event["number"],
                        request_headers,
                    )
                    filtered_pr_event["reviews"] = pr_raw_reviews
                    filtered_pr_events.append(filtered_pr_event)

        query_params["page"] += 1

    return filtered_pr_events


if __name__ == "__main__":
    from json import dumps
    from os import environ

    # Get the GitHub API token from the environment
    repo_url = "https://github.com/burnash/gspread"
    reponse = get_github_repo_pull_requests_filterd_data(repo_url, 30)
    with open("test_github.json", "w") as f:
        f.write(dumps(reponse, indent=4, default=str))
