from matplotlib import pyplot as plt
import math
import json
import pandas

annotated = 600 # Top n top-down issues to look at 
bottomup = 1600 # Top n bottom-up issues to look at

# Gets the n top down issues, can be project specific
def get_top_down_issues(n, project = None):
    CAC = json.load(open('data/ComponentsAndConnectors.json',))
    DF = json.load(open('data/DecisionFactors.json',))
    R = json.load(open('data/Rationale.json',))
    RS = json.load(open('data/ReusableSolutions.json',))

    cac_issues = filter_project(CAC['issues'][:n], project)
    df_issues = filter_project(DF['issues'][:n], project)
    r_issues = filter_project(R['issues'][:n], project)
    rs_issues = filter_project(RS['issues'][:n], project)
        
    return (cac_issues, df_issues, r_issues, rs_issues)

# Gets the n bottom-up issues from excel file, can be project specific
def get_bottom_up_issues(n, project = None):
    xlsx = pandas.ExcelFile("bottom-up-saved.xlsx")

    sheet2 = xlsx.parse(1)

    issues = []

    for i in range(n):
        key = sheet2.iloc[i,0]
        p = (key.split('-'))[0]
        if ((not project) or p == project):
            issue = {}
            issue['key'] = key
            issue['tags'] = []
            if sheet2.iloc[i,2] == 'x':
                issue['tags'].append({
                    'name': 'Existence'
                })
            if sheet2.iloc[i,3] == 'x':
                issue['tags'].append({
                    'name': 'Property'
                })
            if sheet2.iloc[i,4] == 'x':
                issue['tags'].append({
                    'name': 'Executive'
                })
            issues.append(issue)
    
    return issues

# Gets all bottom up issues (KEYS ONLY, NO TAGS)
def get_all_bottom_up_issues():
    xlsx = pandas.ExcelFile("bottom-up-saved.xlsx")

    sheet1 = xlsx.parse(0)

    issue_keys = []

    for i in range(2562):
        key = sheet1.iloc[i,1]
        issue_keys.append(key)
    
    return issue_keys
    
# Filters a list of issues by project
def filter_project(issues, project):
    if not project:
        return issues
    filtered_issues = []
    for issue in issues:
        issue_project = ((issue['key']).split('-'))[0]
        if project == issue_project:
            filtered_issues.append(issue)
        
    return filtered_issues

# Counts unique top-down issues 
def count_issues():
    cac_issues,df_issues,r_issues,rs_issues = get_top_down_issues(annotated)
    all_issues = cac_issues + df_issues + r_issues + rs_issues
    
    unique_issues = []
    for i in range(len(all_issues)):
        if all_issues[i]['key'] not in unique_issues:
            unique_issues.append(all_issues[i]['key'])
    return len(unique_issues)
    
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
    bu_issues = get_bottom_up_issues(bottomup)
    cac_precision = []
    df_precision = []
    r_precision = []
    rs_precision = []
    
    bu_precision = []
    
    for i in range(annotated):
        cac_precision.append(precision_at_n(cac_issues, i, tag))
        df_precision.append(precision_at_n(df_issues, i, tag))
        r_precision.append(precision_at_n(r_issues, i, tag))
        rs_precision.append(precision_at_n(rs_issues, i, tag))

    for i in range(bottomup):
        bu_precision.append(precision_at_n(bu_issues, i, tag))
    
    return (cac_precision, df_precision, r_precision, rs_precision, bu_precision)

# Plots the precision data and saves the figure
def plot_precision_data(tag = ""):
    cac_precision, df_precision, r_precision, rs_precision, bu_precision = generate_precision_data(tag)
    fig, ax = plt.subplots()
    ax.plot(cac_precision, label='Components And Connectors')
    ax.plot(df_precision, label='Descision Factors')
    ax.plot(r_precision, label='Rationale')
    ax.plot(rs_precision, label='Reusable Solutions')
    ax.plot(bu_precision, label='Bottom Up Issues')
    ax.set(xlabel='k', ylabel='Precision')
    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/top_{annotated}_{tag}_precision.png')
    plt.show()

# Finds the average amount of issues over w issues at rank n. Used temporarily, no use for final results
def window_at_n(issues, n, w):
    AK_tags = ['Existence', 'Property', 'Executive']
    if n-w+1 < 0:
        return 0
    relevant = 0
    for i in range(n-w+1,n+1):
        tags = [tag['name'] for tag in issues[i]['tags']]
        if (any(tag in tags for tag in AK_tags) and ('BOTTOMUP' not in tags)):
            relevant += 1
    return relevant

# Generates the window data for use in plotting
def generate_window_data(n):
    cac_issues,df_issues,r_issues,rs_issues = get_top_down_issues(annotated)
    cac_window = []
    df_window = []
    r_window = []
    rs_window = []
    for i in range(annotated):
        cac_window.append(window_at_n(cac_issues, i, n))
        df_window.append(window_at_n(df_issues, i, n))
        r_window.append(window_at_n(r_issues, i, n))
        rs_window.append(window_at_n(rs_issues, i, n))
    return (cac_window, df_window, r_window, rs_window)

# Plots window data and saves the figure
def plot_window_data(n):
    cac_window, df_window, r_window, rs_window = generate_window_data(n)
    fig, ax = plt.subplots()
    ax.plot(cac_window, label='Components And Connectors')
    ax.plot(df_window, label='Descision Factors')
    ax.plot(r_window, label='Rationale')
    ax.plot(rs_window, label='Reusable Solutions')
    ax.set(xlabel='k', ylabel='Relevant in window', title=f'Top {annotated} issues window totals ({n}) ')
    ax.legend()
    plt.savefig(f'figures/top_{annotated}_window.png')
    plt.show()

# Counts the occurences of tag in issues
def get_tag_count(issues, tag):
    count = 0
    for issue in issues:
        for t in issue['tags']:
            if t['name'] == tag:
                count += 1
    return count

# Counts the occurences of the collection of tags in issues
def get_combo_tag_count(issues, tags):
    count = 0
    for issue in issues:
        tags_collected = set()
        for t in issue['tags']:
            if t['name'] != 'ANNOTATED':
                tags_collected.add(t['name'])
        if tags_collected == tags:
            count += 1
    return count

# Counts the occurences of tag in a list of lists of issues 
def get_tag_count_list(issue_list, tag):
    return [get_tag_count(issues, tag) for issues in issue_list]

# For all combinations of tags possible, gets the combionation tag count for the list of issues specified
def get_combo_tag_count_list(issues):
    EXI, PRO, EXE = ('Existence', 'Property', 'Executive')
    tag_combos = [set(x) for x in [[EXI], [PRO], [EXE], [EXI, PRO], [EXI, EXE], [PRO, EXE], [EXI, PRO, EXE]]]
    return [get_combo_tag_count(issues, tags) for tags in tag_combos]
    
# Plots the tag data for each indicidual tag, can be project specific
def plot_tag_data(project = None):
    labels = ['CAC', 'DF', 'R', 'RS', 'Bottom-Up']
    issue_list = list(get_top_down_issues(annotated, project))
    issue_list.append(get_bottom_up_issues(1200, project))
    if not project:
        project = 'All Projects'
    fig, ax = plt.subplots()
    ax.bar(labels, get_tag_count_list(issue_list, 'Existence'), 0.7, label='Existence')
    ax.bar(labels, get_tag_count_list(issue_list, 'Property'), 0.7, bottom = get_tag_count_list(issue_list, 'Existence'), label='Property')
    ax.bar(labels, get_tag_count_list(issue_list, 'Executive'), 0.7, bottom = [sum(x) for x in zip(get_tag_count_list(issue_list, 'Existence'), get_tag_count_list(issue_list, 'Property'))],  label='Executive')
    ax.set_ylabel('tag_count')
    ax.set_title(project)
    ax.legend()
    fig.set_size_inches(4, 4)
    plt.savefig(f'figures/tag_counts_{project}.png')
    plt.show()

# plots the tag data for all combinations of tags, can be project specific. 
def plot_tag_combo_data(project = None):
    EXI, PRO, EXE = ('EXI', 'PRO', 'EXE')
    labels = [f"{EXI}", f"{PRO}", f"{EXE}", f"{EXI}, {PRO}", f"{EXI}, {EXE}", f"{PRO}, {EXE}", "ALL"]
    cac_issues, df_issues, r_issues, rs_issues = get_top_down_issues(annotated, project)

    bu_issues = get_bottom_up_issues(1200, project)

    if not project:
        project = 'All Projects'
    fig, ax = plt.subplots()

    cac_issues_tags = get_combo_tag_count_list(cac_issues)
    df_issues_tags = get_combo_tag_count_list(df_issues)
    r_issues_tags = get_combo_tag_count_list(r_issues)
    rs_issues_tags = get_combo_tag_count_list(rs_issues)
    bu_issues_tags = get_combo_tag_count_list(bu_issues)

    ax.bar(labels, cac_issues_tags, 0.7, label='Components and connectors')
    ax.bar(labels, df_issues_tags, 0.7, bottom = cac_issues_tags, label='Descision factors')
    ax.bar(labels, r_issues_tags, 0.7, bottom = [sum(x) for x in zip(cac_issues_tags, df_issues_tags)], label='Rationale')
    ax.bar(labels, rs_issues_tags, 0.7, bottom = [sum(x) for x in zip(cac_issues_tags, df_issues_tags, r_issues_tags)], label='Reusable solutions')
    ax.bar(labels, bu_issues_tags, 0.7, bottom = [sum(x) for x in zip(cac_issues_tags, df_issues_tags, r_issues_tags, rs_issues_tags)], label='Bottom-up issues')

    ax.set_ylabel('tag_count')
    ax.set_title(project)
    ax.legend()
    fig.set_size_inches(8, 8)
    plt.savefig(f'figures/tag_counts_combos_{project}.png')
    plt.show()

# Calculates the ndcg at ranking n, can be tag specific
def ndcg_at_n(issues, n, tag):
    AK_tags = ['Existence', 'Property', 'Executive']
    if tag:
        AK_tags = [tag]
    if len(issues) < n:
        return ndcg_at_n(issues, len(issues), tag)
    relevance_list = []
    for i in range(n):
        tags = [tag['name'] for tag in issues[i]['tags']]
        if (any(tag in tags for tag in AK_tags) and ('BOTTOMUP' not in tags)):
            relevance_list.append(1)
        else:
            relevance_list.append(0)
    ideal_relevance_list = sorted(relevance_list, reverse=True)
    dcg = 0
    idcg = 0
    for i in range(n):
        dcg += (relevance_list[i])/math.log(i+2, 2)
        idcg += (ideal_relevance_list[i])/math.log(i+2, 2)
    if idcg == 0:
        return 0
    return dcg/idcg

# Prepares NDCG data for plotting
def generate_ndcg_data(tag):
    cac_issues,df_issues,r_issues,rs_issues = get_top_down_issues(annotated)
    bu_issues = get_bottom_up_issues(bottomup)
    cac_ndcg = []
    df_ndcg = []
    r_ndcg = []
    rs_ndcg = []
    bu_ndcg = []
    for i in range(annotated):
        cac_ndcg.append(ndcg_at_n(cac_issues, i, tag))
        df_ndcg.append(ndcg_at_n(df_issues, i, tag))
        r_ndcg.append(ndcg_at_n(r_issues, i, tag))
        rs_ndcg.append(ndcg_at_n(rs_issues, i, tag))
    for i in range(bottomup):
        bu_ndcg.append(ndcg_at_n(bu_issues, i, tag))
        
    return (cac_ndcg, df_ndcg, r_ndcg, rs_ndcg, bu_ndcg)

# plots the NDCG data and saves the figures
def plot_ndcg_data(tag = ""):
    cac_ndcg, df_ndcg, r_ndcg, rs_ndcg, bu_ndcg = generate_ndcg_data(tag)
    fig, ax = plt.subplots()
    ax.plot(cac_ndcg, label='Components And Connectors')
    ax.plot(df_ndcg, label='Descision Factors')
    ax.plot(r_ndcg, label='Rationale')
    ax.plot(rs_ndcg, label='Reusable Solutions')
    ax.plot(bu_ndcg, label='Bottom Up Issues')
    ax.set(xlabel='k', ylabel='NDCG')
    ax.set_title(tag)
    ax.legend()
    fig.set_size_inches(8,4.5)
    plt.savefig(f'figures/top_{annotated}_{tag}_NDCG.png')
    plt.show()

# Saves a json of top down issues, either containing AK or not. 
def make_top_down_issues_json(AK):
    cac_issues,df_issues,r_issues,rs_issues = get_top_down_issues(annotated)
    all_issues = cac_issues + df_issues + r_issues + rs_issues
    
    unique_issues_keys = []
    unique_issues = []
    for i in range(len(all_issues)):
        if all_issues[i]['key'] not in unique_issues_keys:
            unique_issues_keys.append(all_issues[i]['key'])
            unique_issues.append(all_issues[i])
    AK_issues = []
    for issue in unique_issues:
        tags = [tag['name'] for tag in issue['tags']]
        AK_tags = ['Existence', 'Property', 'Executive']
        if (any(tag in tags for tag in AK_tags) == AK) and ('BOTTOMUP' not in tags):
            AK_issues.append(issue)
    output = {
        'issues': AK_issues
    }
    non = 'non-' if not AK else ''
    with open(f"analysis-output/top-down-{non}AK-issues.json", "w") as outfile:
        json.dump(output, outfile)

# Saves a json of bottom up issues, either containing AK or not. 
def make_bottom_up_issues_json(AK):
    issues = get_bottom_up_issues(bottomup)
    AK_issues = []
    for issue in issues:
        tags = [tag['name'] for tag in issue['tags']]
        AK_tags = ['Existence', 'Property', 'Executive']
        if any(tag in tags for tag in AK_tags) == AK:
            AK_issues.append(issue)
    output = {
        'issues': AK_issues
    }
    non = 'non-' if not AK else ''
    with open(f"analysis-output/bottom-up-{non}AK.json", "w") as outfile:
        json.dump(output, outfile)

# Saves a json of all bottom-up issues found
def make_all_bottom_up_issues_json():
    output = {
        'issues': get_all_bottom_up_issues()
    }
    with open(f"analysis-output/all-bottom-up-issues.json", "w") as outfile:
        json.dump(output, outfile)

print("Total unique top-down issues: " + str(count_issues()))

plot_precision_data()
plot_precision_data("Existence")
plot_precision_data("Property")
plot_precision_data("Executive")
plot_ndcg_data()
plot_ndcg_data('Existence')
plot_ndcg_data('Property')
plot_ndcg_data('Executive')
plot_tag_data()
plot_tag_data('HADOOP')
plot_tag_data('CASSANDRA')
plot_tag_data('HDFS')
plot_tag_data('MAPREDUCE')
plot_tag_data('YARN')
plot_tag_data('TAJO')
plot_tag_combo_data()
make_top_down_issues_json(False)
make_top_down_issues_json(True)
make_bottom_up_issues_json(False)
make_bottom_up_issues_json(True)
make_all_bottom_up_issues_json()