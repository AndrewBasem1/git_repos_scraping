from matplotlib import pyplot as plt
from matplotlib.container import BarContainer
from collections import Counter
import numpy as np


def _create_bar_plot(
    counter: Counter,
    sort_by: str,
    x_label: str,
    y_label: str,
    plot_title: str,
    show_values_on_bars: bool,
    empty_msg: str,
) -> BarContainer:
    if counter is None or len(counter.keys()) == 0:
        print(empty_msg)
        return None
    if not isinstance(counter, Counter):
        raise TypeError("the input must be of type Counter")

    sort_by = sort_by.lower().strip()
    if sort_by == "key":
        sorting_key = lambda item: item[0]
    elif sort_by == "value":
        sorting_key = lambda item: item[1]
    else:
        raise ValueError('sort_by must be either "key" or "value"')

    if len(counter.keys()) > 1:
        counter = Counter(
            dict(
                sorted(
                    counter.items(),
                    key=sorting_key,
                    reverse=True,
                )
            )
        )

    y_values = list(counter.values())
    x_values = list(counter.keys())
    bar_plot = plt.bar(x_values, y_values)
    plt.yticks(ticks=range(0, max(y_values) + 2))
    if show_values_on_bars:
        for bar in bar_plot:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                str(height),
                ha="center",
                va="bottom",
            )
    plt.xlabel(x_label)
    # checking if we need to rotate the x labels
    max_len = max([len(str(x)) for x in x_values])
    if max_len > 8:
        plt.xticks(rotation=90)
    plt.ylabel(y_label)
    plt.title(plot_title)
    plt.show()
    return bar_plot


def _create_grouped_bar_plot(
    dict_of_counters: dict,
    possible_counter_keys: list,
    x_label: str = None,
    y_label: str = None,
    plot_title: str = None,
    show_values_on_bars: bool = None,
    empty_msg: str = None,
) -> BarContainer:
    # TODO: implement this function
    if not isinstance(dict_of_counters, dict):
        raise TypeError("the input must be of type dict")
    all_values_are_counters = all(
        (isinstance(x, Counter) for x in dict_of_counters.values())
    )
    if not all_values_are_counters:
        raise TypeError("all values in the input dict must be of type Counter")

    if len(dict_of_counters.keys()) == 0:
        print(empty_msg)
        return None

    if len(dict_of_counters.keys()) > 1:
        # sort dict by keys
        dict_of_counters = dict(
            sorted(
                dict_of_counters.items(),
                key=lambda item: item[0],
                reverse=True,
            )
        )

    dates = dict_of_counters.keys()
    counters = dict_of_counters.values()
    counter_formatted_values = dict()
    for key in possible_counter_keys:
        counter_formatted_values[key] = [counter.get(key, 0) for counter in counters]

    max_value = max([max(x) for x in counter_formatted_values.values()])
    x_ticks = np.arange(0, len(dates))
    num_bars_per_tick = len(possible_counter_keys)
    bar_width = 1 / (num_bars_per_tick + 1)
    multipler = 0

    fig, ax = plt.subplots()
    ax.set_ylim(0, max_value + 2)

    for key, values in counter_formatted_values.items():
        offset = bar_width * multipler
        rects = ax.bar(x_ticks + offset, values, bar_width, label=key)
        if show_values_on_bars:
            ax.bar_label(rects, padding=3)
        multipler += 1

    # ax.set_ylabel(y_label)
    # ax.set_xlabel(x_label)
    # ax.set_title(plot_title)
    ax.set_xticks(x_ticks + (bar_width * num_bars_per_tick / 2), dates)
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    ax.legend(
        bbox_to_anchor=(0, 1.02, 1, 0.2),
        loc="lower left",
        ncols=4,
    )
    plt.show()


def _create_mutiple_bar_plots(
    dict_of_counters: dict,
    possible_counter_keys: list,
    x_label: str = None,
    y_label: str = None,
    plot_title: str = None,
    show_values_on_bars: bool = None,
    empty_msg: str = None,
) -> BarContainer:
    n_plots = len(dict_of_counters.keys())
    fig, axs = plt.subplots(1, n_plots, sharey=True, sharex=True)
    fig.suptitle("number of str matches per date")
    fig.supylabel("Number of matches")
    plt.yticks(ticks=range(0, 100))
    for ax_num, date_and_counter in enumerate(dict_of_counters.items()):
        date = date_and_counter[0]
        counter = date_and_counter[1]
        for keys_values in counter.items():
            key = keys_values[0]
            values = keys_values[1]
            axs[ax_num].bar(key, values, label=key)
        axs[ax_num].set_title(date, loc="center", y=1)
        axs[ax_num].set_ylim(0, max(counter.values()) + 2)
    plt.show()


def plot_merged_pr_counts_per_day(merged_pr_counter_per_day: Counter) -> BarContainer:
    x_label = "Date"
    y_label = "Number of merged pull requests"
    plot_title = "Number of merged pull requests per day"
    sort_by = "key"
    show_values_on_bars = True
    empty_msg = "No merged pull requests found"
    _create_bar_plot(
        merged_pr_counter_per_day,
        sort_by,
        x_label,
        y_label,
        plot_title,
        show_values_on_bars,
        empty_msg,
    )


def plot_approvers_list(approvers_counter: Counter) -> BarContainer:
    x_label = "Approver"
    y_label = "Number of approvals"
    plot_title = "Number of approvals per approver"
    sort_by = "value"
    show_values_on_bars = True
    empty_msg = "No approvals found"
    _create_bar_plot(
        approvers_counter,
        sort_by,
        x_label,
        y_label,
        plot_title,
        show_values_on_bars,
        empty_msg,
    )


def plot_str_matches(str_matches_counter: Counter) -> BarContainer:
    x_label = "String match"
    y_label = "Number of matches"
    plot_title = "Number of matches per string"
    sort_by = "value"
    show_values_on_bars = True
    empty_msg = "No string matches found"
    _create_bar_plot(
        str_matches_counter,
        sort_by,
        x_label,
        y_label,
        plot_title,
        show_values_on_bars,
        empty_msg,
    )


def plot_str_matches_date_drill_down(
    str_matches_date_counter: dict, str_vars_to_check: list
) -> None:
    x_label = "Date"
    y_label = "Number of matches"
    plot_title = "Number of matches per string per date"
    show_values_on_bars = True
    empty_msg = "No string matches found"
    _create_mutiple_bar_plots(
        str_matches_date_counter,
        str_vars_to_check,
        x_label,
        y_label,
        plot_title,
        show_values_on_bars,
        empty_msg,
    )


if __name__ == "__main__":
    # data from https://allisonhorst.github.io/palmerpenguins/

    # import matplotlib.pyplot as plt
    # import numpy as np

    # species = ("Adelie", "Chinstrap", "Gentoo")
    # penguin_means = {
    #     "Bill Depth": (18.35, 18.43, 14.98),
    #     "Bill Length": (38.79, 48.83, 47.50),
    #     "Flipper Length": (189.95, 195.82, 217.19),
    # }

    # x = np.arange(len(species))  # the label locations
    # width = 0.25  # the width of the bars
    # multiplier = 0

    # fig, ax = plt.subplots(layout="constrained")

    # for attribute, measurement in penguin_means.items():
    #     print(attribute, measurement)
    #     offset = width * multiplier
    #     print(offset)
    #     print(x + offset)
    #     rects = ax.bar(x + offset, measurement, width, label=attribute)
    #     ax.bar_label(rects, padding=3)
    #     multiplier += 1

    # # Add some text for labels, title and custom x-axis tick labels, etc.
    # # ax.set_ylabel("Length (mm)")
    # # ax.set_title("Penguin attributes by species")
    # # ax.set_xticks(x + width, species)
    # # ax.legend(loc="upper left", ncols=3)
    # # ax.set_ylim(0, 250)

    # plt.show()
    # # print(x[0])
    from datetime import date

    test_data = {
        date(2022, 7, 21): Counter(
            {
                "eshta": 1,
                "mashy": 2,
                "yaba": 3,
                "a7aaaaaaaaa nek": 10,
            }
        ),
        date(2022, 7, 25): Counter(
            {
                "eshta": 2,
                "mashy": 2,
                "yaba": 3,
                "a7aaaaaaaaa nek": 10,
            }
        ),
        date(2022, 7, 22): Counter(
            {"eshta": 3, "mashy": 2, "yaba": 3, "a7aaaaaaaaa nek": 10}
        ),
    }
    # import numpy as np

    # x_ticks_labels = list(test_data.keys())
    # x_ticks = np.arange(len(x_ticks_labels))
    # formatted_values_dict = dict()
    # for _str in ["a", "b", "c"]:
    #     formatted_values_dict[_str] = [
    #         test_data[x].get(_str, 0) for x in x_ticks_labels
    #     ]
    # print(formatted_values_dict)
    # fig, ax = plt.subplots()
    # width = 0.25
    # multiplier = 0
    # for _str, values in formatted_values_dict.items():
    #     print(_str, values)
    #     offset = width * multiplier
    #     rects = ax.bar(
    #         x_ticks + offset,
    #         values,
    #         width,
    #         label=_str,
    #     )
    #     ax.bar_label(rects, padding=3)
    #     multiplier += 1
    # plt.show()

    # _create_grouped_bar_plot(
    #     test_data,
    #     ["eshta", "peace", "nek", "zeby", "a7a nek", "yaba", "mashy"],
    #     x_label="Date",
    #     y_label="Number of matches",
    #     plot_title="Number of matches per string",
    #     show_values_on_bars=True,
    #     empty_msg="No string matches found",
    # )
    _create_mutiple_bar_plots(test_data, ["eshta", "mashy", "yaba", "a7aaaaaaaaa nek"])
