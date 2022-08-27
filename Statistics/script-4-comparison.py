from script_shared import add_properties_to_issues, filter_tags, count_property
import json
import matplotlib.pyplot as plt

show_figures = False

def get_AK_issue_VS_data(issue_lists, issue_property, labels = []):
    labels, list_prop_counts = count_property(issue_lists, issue_property, labels)

    issues = []
    # assume all len are the same
    one_len = len(list_prop_counts[0])
    total_len = one_len * len(list_prop_counts)
    for i in range(one_len):
        sum = 0
        for issue_list in list_prop_counts:
            sum += issue_list[i]
        issues.append(sum/total_len * 100) # percentage

    return labels, issues


def get_AK_issues_with_properties(AK, full = False):
    non = 'non-' if not AK else ''
    filenames = ['td_only', 'bu_only', 'mav_only', 'bhat']
    if full:
        filenames = ['td_only', 'bu_only', 'mav_only', 'mav_td', 'mav_bu', 'td_bu', 'all', 'bhat']
    results = []
    for file in filenames:
        results.append(filter_tags(json.load(open(f'analysis-output/issue-sets/{non}AK_{file}.json'))['issues']))
    return results

def plot_AK_vs_non_AK(property):
    # figure out if i can let this be full=True? empty set problem
    issue_lists_AK = get_AK_issues_with_properties(True)
    issue_lists_non_AK = get_AK_issues_with_properties(False)

    AK_labels, AK_issue_counts = get_AK_issue_VS_data(issue_lists_AK, property)
    _, non_AK_issue_counts = get_AK_issue_VS_data(issue_lists_non_AK, property, AK_labels)

    fig, ax = plt.subplots()

    x_labels = ['AK Issues', 'Non-AK Issues']
    for i in range(len(AK_labels)):
        ax.bar(x_labels, [AK_issue_counts[i], non_AK_issue_counts[i]], 0.7, bottom = [sum(AK_issue_counts[:i]), sum(non_AK_issue_counts[:i])], label=AK_labels[i])

    ax.legend()
    # ax.set_ylabel("%")
    plt.title(f"Property '{property}'")
    plt.savefig(f'figures/comparison/AK_vs_non_AK_{property}.png')
    if show_figures:
        plt.show()

def box_plot_AK_vs_non_AK(property):
    issue_lists_AK = get_AK_issues_with_properties(True, True)
    issue_lists_non_AK = get_AK_issues_with_properties(False, True)

    all_AK = []
    for list in issue_lists_AK:
        all_AK += list
    all_non_AK = []
    for list in issue_lists_non_AK:
        all_non_AK += list

    AK_values = [issue[property] for issue in all_AK]
    non_AK_values = [issue[property] for issue in all_non_AK]

    data = [AK_values, non_AK_values]

    fig, ax = plt.subplots()

    ax.boxplot(data)

    plt.xticks([1, 2], ['AK Issues', 'Non-AK Issues'])
    plt.title(f"Property '{property}'")
    plt.savefig(f"figures/comparison/property_'{property}'_box_AK_vs_non-AK.png")
    if show_figures:
        plt.show()


# All the AK vs non-AK issue property comparisons are called here
def AK_vs_non_AK():
    bar_props = ['status', 'resolution', 'is_a_subtask', 'issue_type','hierarchy']
    box_props = ['description_size', 'comment_count', 'average_comment_size', 'attachment_count', 'duration']
    for prop in bar_props:
        plot_AK_vs_non_AK(prop)
    for prop in box_props:
        box_plot_AK_vs_non_AK(prop)

AK_vs_non_AK()