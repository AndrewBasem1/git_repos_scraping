from matplotlib import pyplot as plt
from matplotlib.container import BarContainer
from collections import Counter

def _create_bar_plot(counter:Counter, sort_by:str, x_label:str, y_label:str, plot_title:str, show_values_on_bars:bool, empty_msg:str) -> BarContainer:
    if counter is None or len(counter.keys()) == 0:
        print(empty_msg)
        return None
    if not isinstance(counter,Counter):
        raise TypeError('the input must be of type Counter')
    
    sort_by = sort_by.lower().strip()
    if sort_by == 'key':
        sorting_key = lambda item: item[0]
    elif sort_by == 'value':
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
    bar_plot = plt.bar(x_values,y_values)
    plt.yticks(ticks=range(0,max(y_values)+2))
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
    
def plot_merged_pr_counts_per_day(merged_pr_counter_per_day: Counter) -> BarContainer:
    x_label = 'Date'
    y_label = 'Number of merged pull requests'
    plot_title = 'Number of merged pull requests per day'
    sort_by = 'key'
    show_values_on_bars = True
    empty_msg = 'No merged pull requests found'
    _create_bar_plot(merged_pr_counter_per_day, sort_by, x_label, y_label, plot_title, show_values_on_bars, empty_msg) 

def plot_approvers_list(approvers_counter:Counter) -> BarContainer:
    x_label = 'Approver'
    y_label = 'Number of approvals'
    plot_title = 'Number of approvals per approver'
    sort_by = 'value'
    show_values_on_bars = True
    empty_msg = 'No approvals found'
    _create_bar_plot(approvers_counter, sort_by, x_label, y_label, plot_title, show_values_on_bars, empty_msg)

def plot_str_matches(str_matches_counter:Counter) -> BarContainer:
    x_label = 'String match'
    y_label = 'Number of matches'
    plot_title = 'Number of matches per string'
    sort_by = 'value'
    show_values_on_bars = True
    empty_msg = 'No string matches found'
    _create_bar_plot(str_matches_counter, sort_by, x_label, y_label, plot_title, show_values_on_bars, empty_msg)
