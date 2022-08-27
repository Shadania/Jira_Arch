from matplotlib import pyplot as plt

from script_shared import annotated, bottomup
from script_shared import get_top_down_issues, get_maven_issues, get_bottom_up_issues

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
    ax.plot(cac_precision, label='Components And Connectors')
    ax.plot(df_precision, label='Descision Factors')
    ax.plot(r_precision, label='Rationale')
    ax.plot(rs_precision, label='Reusable Solutions')
    ax.plot(bu_precision, label='Bottom Up Issues')
    ax.plot(maven_added_prec, label='Maven Issues: Added')
    ax.plot(maven_removed_prec, label='Maven Issues: Removed')
    ax.plot(maven_changed_prec, label='Maven Issues: Changed')
    ax.plot(maven_total_prec, label='Maven Issues: Total')
    ax.set(xlabel='k', ylabel='Precision')
    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/precision/top_{annotated}_{tag}_precision.png')
    if show_figures:
        plt.show()

    fig, ax = plt.subplots()
    ax.plot(maven_added_prec, label='Maven Issues: Added')
    ax.plot(maven_removed_prec, label='Maven Issues: Removed')
    ax.plot(maven_changed_prec, label='Maven Issues: Changed')
    ax.plot(maven_total_prec, label='Maven Issues: Total')
    ax.set(xlabel='k', ylabel='Precision')
    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/precision/maven_{tag}_precision.png')
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
    labels = ['CAC', 'DF', 'R', 'RS', 'Bottom-Up', 'MVN-Add', 'MVN-Rem', 'MVN-Cha', 'MVN-Tot']
    issue_list = list(get_top_down_issues(annotated, project))
    issue_list.append(get_bottom_up_issues(1200, project))
    issue_list.extend(get_maven_issues(project))
    if not project:
        project = 'All Projects'
    fig, ax = plt.subplots()
    ax.bar(labels, get_tag_count_list(issue_list, 'Existence'), 0.7, label='Existence')
    ax.bar(labels, get_tag_count_list(issue_list, 'Property'), 0.7, bottom = get_tag_count_list(issue_list, 'Existence'), label='Property')
    ax.bar(labels, get_tag_count_list(issue_list, 'Executive'), 0.7, bottom = [sum(x) for x in zip(get_tag_count_list(issue_list, 'Existence'), get_tag_count_list(issue_list, 'Property'))],  label='Executive')
    ax.set_ylabel('tag_count')
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