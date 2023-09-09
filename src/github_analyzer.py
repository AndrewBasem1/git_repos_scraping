from collections import Counter
from datetime import datetime
from matplotlib import pyplot as plt


def analyze_pr_data(pr_filtered_data: dict, str_vars_to_check: list | str = None):
    """
    This function analyzes the pull request data and answers the following questions:
    1. How many pull requests were merged each day?
    2. How many pull requests were approved by each user?
    3. How many pull requests had a match with any string from a list of input strings?

    # Parameters
    pr_filtered_data: list
        A list of pull request dictionaries, as returned by `get_repo_pull_requests_filterd_data`.
    str_vars_to_check: list|str
        A list of strings (or a single string) to check if they are in the title or body of the pull request.

    # Returns
    A dictionary with the following keys:
    - `pr_counter_per_day`: A dictionary with the number of pull requests merged each day.
    - `approvers_counter`: A dictionary with the number of pull requests approved by each user.
    - `str_matches_counter`: A dictionary with the number of pull requests that had a match with any string from a list of input strings.
    """
    merged_pr_counter_per_day = Counter()

    # NOTE: this is added if we need to drill down in how many approvals did each user give in each day (not needed for now)
    approvals_dict = {}

    approvers_counter = Counter()

    str_matches_counter = Counter()

    for pr in pr_filtered_data:
        # question 1
        merged_at: datetime = pr["merged_at"]
        if merged_at is None:
            pass
        else:
            merged_at_date = merged_at.date()
            merged_at_str = str(merged_at_date)
            merged_pr_counter_per_day [merged_at_str] += 1
            pass

        # question 2
        reviews: list = pr["reviews"]
        if len(reviews) == 0:
            pass
        else:
            for review in reviews:
                if review["state"] == "APPROVED":
                    username = review["username"]
                    approvers_counter[username] += 1
                    submitted_at = review["submitted_at"]
                    submitted_at_str = str(submitted_at.date())
                    if submitted_at not in approvals_dict:
                        approvals_dict[submitted_at_str] = Counter()
                        pass
                    approvals_dict[submitted_at_str][username] += 1
                    pass
                else:
                    pass
            pass

        # question 3
        if str_vars_to_check is None:
            continue
        if isinstance(str_vars_to_check, str):
            str_vars_to_check = [str_vars_to_check]
        title = pr["title"].lower()
        body = pr["body"].lower()
        for str_var in str_vars_to_check:
            if str_var in title or str_var in body:
                str_matches_counter[str_var] += 1

    analysis_results = {
        "merged_pr_counter_per_day": merged_pr_counter_per_day,
        "approvers_counter": approvers_counter,
        "str_matches_counter": str_matches_counter,
    }
    
    return analysis_results

def plot_merged_pr_counts_per_day(merged_pr_counter_per_day:Counter):
    if not(isinstance(merged_pr_counter_per_day, Counter)):
        raise TypeError("merged_pr_counter_per_day must be a Counter object")
    if len(merged_pr_counter_per_day) == 0:
        print('there was no pull requests merged in the requested timeframe')
        return None
    
    # sorting the counter by date (the key)
    if len(merged_pr_counter_per_day.keys()) > 1:
        merged_pr_counter_per_day = Counter(dict(sorted(merged_pr_counter_per_day.items(), key=lambda item: item[0], reverse=True)))
    
    # plotting the data in a bar chart using matplotlib
    dates = list(merged_pr_counter_per_day.keys())
    counts = list(merged_pr_counter_per_day.values())
    print(counts)
    print(type(counts[0]))
    bar_plot = plt.bar(dates, counts)
    plt.yticks(ticks=range(0, max(counts)+2))
    # show y values on the bars
    for bar in bar_plot:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height, str(height), ha='center', va='bottom')
    # plt.xticks(rotation=80)
    plt.xlabel('Date')
    plt.ylabel('Number of merged pull requests')
    plt.title('Number of merged pull requests per day')
    plt.show()
    return bar_plot
    