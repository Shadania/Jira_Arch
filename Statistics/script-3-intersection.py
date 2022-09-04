import json
import matplotlib.pyplot as plt

show_figures = False

from script_shared import filter_tags, count_property, colors, hatches
from script_shared import box_scale, box_show_outliers, graph_colors


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



def plot_method_type_yield(issue_list, filename):
    # separate it out into projects
    data = {}
    types = ['Executive', 'Property', 'Existence']
    for issue in issue_list:
        project = issue['key'].split('-')[0]
        if project not in data:
            data[project] = {}
        for tag in issue['tags']:
            if tag['name'] in types:
                thisTag = tag['name']
                if thisTag not in data[project]:
                    data[project][thisTag] = 0
                data[project][thisTag] += 1

    projects = data.keys()

    x_labels = [project.title() for project in projects]

    fig, ax = plt.subplots()

    heights = []

    for i in range(len(types)):
        bottoms = [0] * len(projects)

        for prev in heights:
            for j in range(len(prev)):
                bottoms[j] += prev[j]

        heights.append([])
        for project in projects:
            if types[i] in data[project]:
                heights[i].append(data[project][types[i]])
            else:
                heights[i].append(0)

        if graph_colors:
            ax.bar(x_labels, heights[i], 0.7, bottom = bottoms, label=types[i], color=colors[i])
        else:
            ax.bar(x_labels, heights[i], 0.7, bottom = bottoms, label=types[i], fill=False, hatch=hatches[i])

    ax.set_ylabel("Tag Count")
    ax.legend()
    plt.title(f"Method Yields: {filename}")

    plt.savefig(f'figures/intersection/method_comparison_{filename}.png')
    if show_figures:
        plt.show()


def plot_property_comparison(issue_lists, issue_property, graph_labels, filename=""):
    # prop_lists: td, bu, mav, mav_td, mav_bu, td_bu, all, bhat
    labels, prop_lists = count_property(issue_lists, issue_property)

    # Settings for Which Labels to Merge
    merged_labels = { # property -> {new label -> [old labels]}
        "resolution": {
            "Fixed": ["Fixed", "Won't Fix"],
            "Not Fixed": ["Duplicate", "None"]
        }
    }

    # Merge Labels according to Settings
    if issue_property in merged_labels:
        this_prop = merged_labels[issue_property]
        for label in this_prop:
            # this is the target label
            # we need to count up the values of the array to arrive at final value
            oldIdx = []
            for val in this_prop[label]:
                if val not in labels:
                    continue
                oldIdx.append(labels.index(val))
                labels.pop(labels.index(val))
            if len(oldIdx) == 0:
                continue
            labels.append(label)
            oldIdx.sort(reverse=True)
            for prop_list in prop_lists:
                newVal = 0.0
                for idx in oldIdx:
                    newVal += prop_list.pop(idx)
                prop_list.append(newVal)

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
        if graph_colors:
            ax.bar(r[idx], prop_list, width=barWidth, label=graph_labels[idx], color=colors[idx])
        else:
            ax.bar(r[idx], prop_list, width=barWidth, label=graph_labels[idx], fill=False, hatch=hatches[idx])
        idx += 1
    
    ax.set_title(F"Property '{issue_property}'")
    ax.set_ylabel("Percentage of found issues")
    plt.xticks(x_axis_ticks, labels)
    fig.set_size_inches(2+2*len(labels), 4)
    ax.legend()
    plt.savefig(f"figures/intersection/property_'{issue_property}'{filename}.png")
    if show_figures:
        plt.show()

def box_plot_property_distribution(issue_lists, issue_property, graph_labels, ylabel, filename = ""):
    values = []
    for issue_list in issue_lists:
        values.append([issue[issue_property] for issue in issue_list])

    fig, ax = plt.subplots()
    # ax.boxplot(values, showfliers=False)
    ax.boxplot(values, showfliers=box_show_outliers)
    ax.set_yscale(box_scale)
    ax.set_ylabel(ylabel)
    
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
    properties_box_ylabel = ["Length in Characters", "Amount of Comments", "Average Size in Characters", "Amount", "Duration in Days"]

    # with intersection
    graph_labels = ['Keywords Searches', 'Static SC Analysis', 'Maven Dependencies', 'Maven & Keywords', 'Maven & SSC', 'Keywords & SSC', 'Full Overlap', 'Random']
    for property in properties_bar:
        plot_property_comparison(lists, property, graph_labels, "_intersection")
    box_labels = ['KW', 'SSC', 'MAV', 'MAV-KW', 'MAV-SSC', 'KW-SSC', 'ALL', 'RANDOM']
    for i in range(len(properties_box)):
        box_plot_property_distribution(lists, properties_box[i], box_labels, properties_box_ylabel[i], "_intersection")

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
    graph_labels = ['Keywords Searches', 'Static SC Analysis', 'Maven Dependencies', 'Random']
    for property in properties_bar:
        plot_property_comparison(lists, property, graph_labels)
    graph_labels = ['Keywords', 'SC Analysis', 'Maven', 'Random']
    for i in range(len(properties_box)):
        box_plot_property_distribution(lists, properties_box[i], graph_labels, properties_box_ylabel[i])

    plot_method_type_yield(td, "Keywords Searches")
    plot_method_type_yield(bu, "Static SC Analysis")
    plot_method_type_yield(mav, "Maven Dependencies")


AK = True
plot_comparisons(AK)