import json
import matplotlib.pyplot as plt

show_figures = False

from script_shared import filter_tags, add_properties_to_issues, count_property


# Gets the issue sets with saved properties, depending on the argument, which can be either AK or non-AK
def get_AK_issues_with_properties(AK):
    non = 'non-' if not AK else ''
    td_path = f"analysis-output/issue-sets/{non}AK_td_only.json"
    bu_path = f"analysis-output/issue-sets/{non}AK_bu_only.json"
    mav_path = f"analysis-output/issue-sets/{non}AK_mav_only.json"

    mav_td_path = f"analysis-output/issue-sets/{non}AK_mav_td.json"
    mav_bu_path = f"analysis-output/issue-sets/{non}AK_mav_bu.json"
    td_bu_path = f"analysis-output/issue-sets/{non}AK_td_bu.json"

    all_path = f"analysis-output/issue-sets/{non}AK_all.json"

    bhat_path = f"analysis-output/issue-sets/{non}AK_bhat.json"

    td = filter_tags((json.load(open(td_path)))['issues'])
    bu = filter_tags((json.load(open(bu_path)))['issues'])
    mav = filter_tags((json.load(open(mav_path)))['issues'])

    td_bu = filter_tags((json.load(open(td_bu_path)))['issues'])
    mav_td = filter_tags((json.load(open(mav_td_path)))['issues'])
    mav_bu = filter_tags((json.load(open(mav_bu_path)))['issues'])
    
    all = filter_tags((json.load(open(all_path)))['issues'])
    bhat = filter_tags((json.load(open(bhat_path)))['issues'])

    return (td, bu, mav, mav_td, mav_bu, td_bu, all, bhat)




def plot_property_comparison(issue_lists, issue_property, graph_labels, filename=""):
    # prop_lists: td, bu, mav, mav_td, mav_bu, td_bu, all, bhat
    labels, prop_lists = count_property(issue_lists, issue_property)
    """
    if issue_property == "status":
        with open('output.json','w+') as outfile:
            json.dump(prop_lists, outfile)
        closedIdx = -1
        resolvedIdx = -1
        for i in range(len(labels)):
            if labels[i].lower() == 'closed':
                closedIdx = i
            if labels[i].lower() == 'resolved':
                resolvedIdx = i
        if closedIdx == -1 or resolvedIdx == -1:
            print("Something went wrong.")
        else:
            # we need to merge these
            labels.pop(resolvedIdx)
            for issue_list in prop_lists:
                print(issue_list[closedIdx])
                issue_list[closedIdx] += issue_list[resolvedIdx]
                issue_list.pop(resolvedIdx)
    """

    barWidth = 0.25

    prop_lists = prop_lists

    x_axis_ticks = [(x + 0.5) * ((1 + len(prop_lists))*barWidth) for x in range(len(labels))]

    r = []
    r.append([x - 0.5*len(prop_lists)*barWidth + 0.5*barWidth for x in x_axis_ticks])
    idx = 1
    for prop_list in prop_lists:
        r.append([x + barWidth for x in r[idx-1]])
        idx += 1

    fig, ax = plt.subplots()

    idx = 0
    for prop_list in prop_lists:
        ax.bar(r[idx], prop_list, width=barWidth, label=graph_labels[idx])
        idx += 1
    
    ax.set_title(F"Property '{issue_property}'")
    ax.set_ylabel("%")
    plt.xticks(x_axis_ticks, labels)
    fig.set_size_inches(2+2*len(labels), 4)
    ax.legend()
    plt.savefig(f"figures/intersection/property_'{issue_property}'{filename}.png")
    if show_figures:
        plt.show()

def box_plot_property_distribution(issue_lists, issue_property, graph_labels, filename = ""):
    values = []
    for issue_list in issue_lists:
        values.append([issue[issue_property] for issue in issue_list])

    fig, ax = plt.subplots()
    ax.boxplot(values)
    
    xticks = [x+1 for x in range(len(graph_labels))]

    plt.xticks(xticks, graph_labels)
    plt.title(f"Property '{issue_property}'")
    plt.savefig(f"figures/intersection/property_'{issue_property}'_box{filename}.png")

    if show_figures:
        plt.show()

def plot_comparisons(AK):
    td, bu, mav, mav_td, mav_bu, td_bu, all, bhat = get_AK_issues_with_properties(AK)
    lists = [td, bu, mav, mav_td, mav_bu, td_bu, all, bhat]

    properties_bar = ['status','resolution','is_a_subtask','issue_type','hierarchy']
    properties_box = ['description_size','comment_count','average_comment_size','attachment_count', 'duration']

    # with intersection
    graph_labels = ['Top Down', 'Bottom Up', 'Maven', 'Maven & Top Down', 'Maven & Bottom Up', 'Top Down & Bottom Up', 'Full Overlap', 'Random']
    for property in properties_bar:
        plot_property_comparison(lists, property, graph_labels, "_intersection")
    box_labels = ['TD', 'BU', 'MAV', 'MAV-TD', 'MAV-BU', 'TD-BU', 'ALL', 'RANDOM']
    for property in properties_box:
        box_plot_property_distribution(lists, property, box_labels, "_intersection")

    # without intersection
    for issue in mav_td:
        td.append(issue)
        mav.append(issue)
    for issue in mav_bu:
        bu.append(issue)
        mav.append(issue)
    for issue in td_bu:
        td.append(issue)
        bu.append(issue)
    for issue in all:
        mav.append(issue)
        td.append(issue)
        bu.append(issue)

    lists = [td, bu, mav, bhat]
    graph_labels = ['Top Down', 'Bottom Up', 'Maven', 'Random']
    for property in properties_bar:
        plot_property_comparison(lists, property, graph_labels)
    for property in properties_box:
        box_plot_property_distribution(lists, property, graph_labels)


AK = True
plot_comparisons(AK)