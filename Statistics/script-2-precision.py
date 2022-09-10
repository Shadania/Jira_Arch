from matplotlib import pyplot as plt

from script_shared import annotated, bottomup
from script_shared import get_top_down_issues, get_maven_issues, get_bottom_up_issues, colors, plot_styles, hatches
from script_shared import box_scale, box_show_outliers, graph_colors

import numpy

show_figures = False


# From a list of issues, gets the precision at the n'th rank. Can be for a specific tag. 
def precision_at_n(issues, n, tag):
    AK_tags = ['Existence', 'Property', 'Executive']
    if tag:
        AK_tags = [tag]
    if n == 0:
        return 1
    if len(issues) < n:
        return precision_at_n(issues, len(issues), tag)
    relevant = 0
    for i in range(n):
        tags = [tag['name'] for tag in issues[i]['tags']]
        if (any(tag in tags for tag in AK_tags) and ('BOTTOMUP' not in tags)):
            relevant += 1
    return relevant/n

# Gets precision lists for all issues at all n's, and can be for a specific tag as well
def generate_precision_data(tag):
    cac_issues,df_issues,r_issues,rs_issues = get_top_down_issues(annotated)
    cac_precision = []
    df_precision = []
    r_precision = []
    rs_precision = []
    
    bu_issues = get_bottom_up_issues(bottomup)
    bu_precision = []

    maven_added, maven_removed, maven_changed, maven_total = get_maven_issues()
    maven_added_prec = []
    maven_removed_prec = []
    maven_changed_prec = []
    maven_total_prec = []

    for i in range(annotated):
        cac_precision.append(precision_at_n(cac_issues, i, tag))
        df_precision.append(precision_at_n(df_issues, i, tag))
        r_precision.append(precision_at_n(r_issues, i, tag))
        rs_precision.append(precision_at_n(rs_issues, i, tag))

    for i in range(bottomup):
        bu_precision.append(precision_at_n(bu_issues, i, tag))

    for i in range(len(maven_added)):
        maven_added_prec.append(precision_at_n(maven_added, i, tag))
    for i in range(len(maven_removed)):
        maven_removed_prec.append(precision_at_n(maven_removed, i, tag))
    for i in range(len(maven_changed)):
        maven_changed_prec.append(precision_at_n(maven_changed, i, tag))
    for i in range(len(maven_total)):
        maven_total_prec.append(precision_at_n(maven_total, i, tag))
    
    return (cac_precision, df_precision, r_precision, rs_precision, bu_precision, maven_added_prec, maven_removed_prec, maven_changed_prec, maven_total_prec)

# Plots the precision data and saves the figure
def plot_precision_data(tag = ""):
    cac_precision, df_precision, r_precision, rs_precision, bu_precision, maven_added_prec, maven_removed_prec, maven_changed_prec, maven_total_prec = generate_precision_data(tag)
    fig, ax = plt.subplots()

    to_plot = [cac_precision, df_precision, r_precision, rs_precision, bu_precision, maven_added_prec, maven_removed_prec, maven_changed_prec, maven_total_prec]
    labels = [
        'Keywords: Components And Connectors',
        'Keywords: Descision Factors',
        'Keywords: Rationale',
        'Keywords: Reusable Solutions',
        'Static SC Analysis',
        'Maven Dependencies: Added',
        'Maven Dependencies: Removed',
        'Maven Dependencies: Changed',
        'Maven Dependencies: Total'
    ]

    for i in range(len(to_plot)):
        if graph_colors:
            ax.plot(to_plot[i], label=labels[i], color=colors[i])
        else:
            color = '#000000'
            if i > 4:
                color = '#808080'
            ax.plot(to_plot[i], plot_styles[i], label=labels[i], color=color)

    ax.set(xlabel='k', ylabel='Precision')
    xticks = ax.get_xticks()[1:]
    xticks[0] = 1
    ax.set_xticks(xticks)

    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/precision/top_{annotated}_{tag}_precision.png')
    if show_figures:
        plt.show()

    fig, ax = plt.subplots()
    if graph_colors:
        ax.plot(maven_added_prec, label='Maven Dependencies: Added', color=colors[0])
        ax.plot(maven_removed_prec, label='Maven Dependencies: Removed', color=colors[1])
        ax.plot(maven_changed_prec, label='Maven Dependencies: Changed', color=colors[2])
        ax.plot(maven_total_prec, label='Maven Dependencies: Total', color=colors[3])
    else:
        ax.plot(maven_added_prec, plot_styles[0], label='Maven Dependencies: Added', color='#000000')
        ax.plot(maven_removed_prec, plot_styles[1], label='Maven Dependencies: Removed', color='#000000')
        ax.plot(maven_changed_prec, plot_styles[2], label='Maven Dependencies: Changed', color='#000000')
        ax.plot(maven_total_prec, plot_styles[3], label='Maven Dependencies: Total', color='#000000')
    ax.set(xlabel='k', ylabel='Precision')
    xticks = ax.get_xticks()[1:]
    xticks[0]=1
    ax.set_xticks(xticks)
    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/precision/maven_{tag}_precision.png')
    if show_figures:
        plt.show()


def plot_average_precision_data(tag = ""):
    cac_precision, df_precision, r_precision, rs_precision, bu_precision, maven_added_prec, maven_removed_prec, maven_changed_prec, maven_total_prec = generate_precision_data(tag)

    # average out the keywords precision data
    max_k = len(maven_total_prec)
    keywords_precision = []
    for i in range(len(cac_precision)):
        if i >= max_k:
            break
        keywords_precision.append((cac_precision[i] + df_precision[i] + r_precision[i] + rs_precision[i]) * 0.25)

    if len(bu_precision) > max_k:
        bu_precision = bu_precision[:max_k]

    fig, ax = plt.subplots()

    if graph_colors:
        ax.plot(keywords_precision, label='Keywords Searches', color=colors[0])
        ax.plot(maven_total_prec, label='Maven Dependencies', color=colors[1])
        ax.plot(bu_precision, label='Static SC Analysis', color=colors[2])
    else:
        ax.plot(keywords_precision, plot_styles[0], label='Keywords Searches', color='#000000')
        ax.plot(maven_total_prec, plot_styles[1], label='Maven Dependencies', color='#000000')
        ax.plot(bu_precision, plot_styles[2], label='Static SC Analysis', color='#000000')

    ax.set(xlabel='k', ylabel='Precision')
    xticks = ax.get_xticks()[1:]
    xticks[0] = 1
    ax.set_xticks(xticks)
    ax.set_title(tag)
    ax.legend()

    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/precision/average_{tag}_precision.png')
    if show_figures:
        plt.show()

def plot_limited_precision_data(tag = ""):
    cac_precision, df_precision, r_precision, rs_precision, bu_precision, maven_added_prec, maven_removed_prec, maven_changed_prec, maven_total_prec = generate_precision_data(tag)

    max_k = len(maven_total_prec)
    for maven_list in [maven_added_prec, maven_removed_prec, maven_changed_prec]:
        if len(maven_list) < max_k:
            max_k = len(maven_list)
    
    maven_added_prec = maven_added_prec[:max_k]
    maven_removed_prec = maven_removed_prec[:max_k]
    maven_changed_prec = maven_changed_prec[:max_k]
    
    fig, ax = plt.subplots()
    if graph_colors:
        ax.plot(maven_added_prec, label='Maven Dependencies: Added', color=colors[0])
        ax.plot(maven_removed_prec, label='Maven Dependencies: Removed', color=colors[1])
        ax.plot(maven_changed_prec, label='Maven Dependencies: Changed', color=colors[2])
    else:
        ax.plot(maven_added_prec, plot_styles[0], label='Maven Dependencies: Added', color='#000000')
        ax.plot(maven_removed_prec, plot_styles[1], label='Maven Dependencies: Removed', color='#000000')
        ax.plot(maven_changed_prec, plot_styles[2], label='Maven Dependencies: Changed', color='#000000')

    xticks = ax.get_xticks()[1:]
    xticks[0] = 1
    ax.set_xticks(xticks)
    ax.set(xlabel='k', ylabel='Precision')
    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/precision/maven_limited_{tag}_precision.png')
    if show_figures:
        plt.show()

def plot_query_precision_data(tag = ""):
    cac_precision, df_precision, r_precision, rs_precision, bu_precision, maven_added_prec, maven_removed_prec, maven_changed_prec, maven_total_prec = generate_precision_data(tag)
    fig, ax = plt.subplots()

    max_k = 600
    cac_precision = cac_precision[:max_k]
    df_precision = df_precision[:max_k]
    r_precision = r_precision[:max_k]
    rs_precision = rs_precision[:max_k]

    if graph_colors:
        ax.plot(cac_precision, label='Components And Connectors', color=colors[0])
        ax.plot(df_precision, label='Descision Factors', color=colors[1])
        ax.plot(r_precision, label='Rationale', color=colors[2])
        ax.plot(rs_precision, label='Reusable Solutions', color=colors[3])
    else:
        ax.plot(cac_precision, plot_styles[0], label='Components And Connectors', color='#000000')
        ax.plot(df_precision, plot_styles[1], label='Descision Factors', color='#000000')
        ax.plot(r_precision, plot_styles[2], label='Rationale', color='#000000')
        ax.plot(rs_precision, plot_styles[3], label='Reusable Solutions', color='#000000')

    xticks = ax.get_xticks()[1:]
    xticks[0] = 1
    ax.set_xticks(xticks)
    ax.set(xlabel='k', ylabel='Precision')
    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/precision/queries_precision.png')
    if show_figures:
        plt.show()

# Counts the occurences of tag in issues
def get_tag_count(issues, tag):
    count = 0
    for issue in issues:
        for t in issue['tags']:
            if t['name'] == tag:
                count += 1
    return count

# Counts the occurences of tag in a list of lists of issues 
def get_tag_count_list(issue_list, tag):
    return [get_tag_count(issues, tag) for issues in issue_list]

# Plots the tag data for each indicidual tag, can be project specific
def plot_tag_data(project = None):
    labels = ['KW-CAC', 'KW-DF', 'KW-R', 'KW-RS', 'SSC', 'MVN-Add', 'MVN-Rem', 'MVN-Cha', 'MVN-Tot']
    issue_list = list(get_top_down_issues(annotated, project))
    issue_list.append(get_bottom_up_issues(1200, project))
    issue_list.extend(get_maven_issues(project))
    if not project:
        project = 'All Projects'
    fig, ax = plt.subplots()

    if graph_colors:
        ax.bar(labels, get_tag_count_list(issue_list, 'Existence'), 0.7, label='Existence', color=colors[0])
        ax.bar(labels, get_tag_count_list(issue_list, 'Property'), 0.7, bottom = get_tag_count_list(issue_list, 'Existence'), label='Property', color=colors[1])
        ax.bar(labels, get_tag_count_list(issue_list, 'Executive'), 0.7, bottom = [sum(x) for x in zip(get_tag_count_list(issue_list, 'Existence'), get_tag_count_list(issue_list, 'Property'))],  label='Executive', color=colors[2])
    else:
        ax.bar(labels, get_tag_count_list(issue_list, 'Existence'), 0.7, label='Existence', fill=False, hatch=hatches[0])
        ax.bar(labels, get_tag_count_list(issue_list, 'Property'), 0.7, bottom = get_tag_count_list(issue_list, 'Existence'), label='Property', fill=False, hatch=hatches[1])
        ax.bar(labels, get_tag_count_list(issue_list, 'Executive'), 0.7, bottom = [sum(x) for x in zip(get_tag_count_list(issue_list, 'Existence'), get_tag_count_list(issue_list, 'Property'))],  label='Executive', fill=False, hatch=hatches[2])
    
    
    ax.set_ylabel('Tag Count')
    ax.set_title(project)
    ax.legend()
    fig.set_size_inches(10, 4)
    plt.savefig(f'figures/precision/tag_counts_{project}.png')
    if show_figures:
        plt.show()


plot_precision_data()
plot_precision_data("Existence")
plot_precision_data("Property")
plot_precision_data("Executive")

plot_tag_data()
plot_tag_data('HADOOP')
plot_tag_data('CASSANDRA')
plot_tag_data('HDFS')
plot_tag_data('MAPREDUCE')
plot_tag_data('YARN')
plot_tag_data('TAJO')


plot_average_precision_data()
for dec_type in ["Existence", "Executive", "Property"]:
    plot_average_precision_data(dec_type)

plot_limited_precision_data()
plot_query_precision_data()
