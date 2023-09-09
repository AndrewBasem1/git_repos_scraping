from matplotlib import pyplot as plt
from matplotlib.container import BarContainer
from collections import Counter


def plot_merged_pr_counts_per_day(merged_pr_counter_per_day: Counter) -> BarContainer:
    if not (isinstance(merged_pr_counter_per_day, Counter)):
        raise TypeError("merged_pr_counter_per_day must be a Counter object")
    if len(merged_pr_counter_per_day) == 0:
        print("there was no pull requests merged in the requested timeframe")
        return None

    # sorting the counter by date (the key)
    if len(merged_pr_counter_per_day.keys()) > 1:
        merged_pr_counter_per_day = Counter(
            dict(
                sorted(
                    merged_pr_counter_per_day.items(),
                    key=lambda item: item[0],
                    reverse=True,
                )
            )
        )

    # plotting the data in a bar chart using matplotlib
    dates = list(merged_pr_counter_per_day.keys())
    counts = list(merged_pr_counter_per_day.values())
    print(counts)
    print(type(counts[0]))
    bar_plot = plt.bar(dates, counts)
    plt.yticks(ticks=range(0, max(counts) + 2))
    # show y values on the bars
    for bar in bar_plot: 
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            str(height),
            ha="center",
            va="bottom",
        )
    # plt.xticks(rotation=80)
    plt.xlabel("Date")
    plt.ylabel("Number of merged pull requests")
    plt.title("Number of merged pull requests per day")
    plt.show()
    return bar_plot

def plot_approvers_list(approvers_counter:Counter) -> BarContainer:
    if not isinstance(approvers_counter,Counter):
        raise TypeError()