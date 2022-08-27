import json
import os
from nltk.corpus import stopwords
from datetime import datetime
from jira import JIRA
jira = JIRA('https://issues.apache.org/jira')
import pandas

annotated = 600 # Top n top-down issues to look at 
bottomup = 1600 # Top n bottom-up issues to look at

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

# Gets the n top down issues, can be project specific
def get_top_down_issues(n, project = None):
    CAC = json.load(open('data/topdown/ComponentsAndConnectors.json',))
    DF = json.load(open('data/topdown/DecisionFactors.json',))
    R = json.load(open('data/topdown/Rationale.json',))
    RS = json.load(open('data/topdown/ReusableSolutions.json',))

    cac_issues = filter_project(CAC['issues'][:n], project)
    df_issues = filter_project(DF['issues'][:n], project)
    r_issues = filter_project(R['issues'][:n], project)
    rs_issues = filter_project(RS['issues'][:n], project)

    return (cac_issues, df_issues, r_issues, rs_issues)

# Gets the n bottom-up issues from excel file, can be project specific
def get_bottom_up_issues(n, project = None):
    xlsx = pandas.ExcelFile("data/bottomup/bottom-up-saved.xlsx")

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

def get_maven_issues(project = None):
    issues = {
        'added': [],
        'removed': [],
        'changed': [],
        'total': []
    }
    for file in ['added.csv', 'removed.csv', 'changed.csv', 'total.csv']:
        first = True
        with open('data/maven/' + file, 'r') as f:
            for line in f:
                if first:
                    first = False
                    continue

                csv = line.strip().split(',')
                if project:
                    if project != csv[0].split('-')[0]:
                        continue
                newIssue = {'key': csv[0], 'tags': []}
                for i in [5, 6, 7]:
                    if len(csv) > i:
                        if csv[i]:
                            newIssue['tags'].append({'name': csv[i]})

                issues[file.split('.')[0]].append(newIssue)

    return (issues['added'], issues['removed'], issues['changed'], issues['total'])


# Generate qualitative data
def count_property(issue_lists, issue_property, static_labels=[], cutoff=0.05, raw_count=False):
    labels = set()
    idx = 0

    # count all different labels per list and keep track of different labels
    properties = []
    for issue_list in issue_lists:
        properties.append({})
        for issue in issue_list:
            val = issue[issue_property]
            if val not in properties[idx]:
                properties[idx][val] = 0
            properties[idx][val] += 1
            labels.add(val)
        idx += 1

    labels = list(labels)

    property_count = []
    for issue_list in issue_lists:
        property_count.append([])
    
    # Normalize data & return if static_labels is set
    if static_labels:
        for label in static_labels:
            idx = 0
            for issue_list in issue_lists:
                property_count[idx].append((properties[idx].get(label, 0)/(1 if raw_count else len(issue_list)*100)))
                idx += 1
        return labels, property_count

    # Else generate off what we have
    for label in labels:
        idx = 0
        for issue_list in issue_lists:
            property_count[idx].append((properties[idx].get(label, 0)/(1 if raw_count else len(issue_list)*100)))
            idx += 1
    
    property_count_all = []
    for issue_list in property_count:
        property_count_all += issue_list
    max_value = max(property_count_all)

    # new addition!
    # due to some of bhat's data not being 100% available anymore for some reason
    # the property_count will be zero-filled
    max_len = len(labels)
    for issue_list in property_count:
        while len(issue_list) < max_len:
            issue_list.append(0.0)


    f_labels = []
    f_property_count = []
    for issue_list in issue_lists:
        f_property_count.append([])
    
    for i in range(len(labels)):
        this_label = []
        for property_count_el in property_count:
            this_label.append(property_count_el[i])
        this_label = tuple(this_label)

        if max(this_label) > cutoff*max_value:
            f_labels.append(labels[i])
            idx = 0
            for issue_list in issue_lists:
                f_property_count[idx].append(property_count[idx][i])
                idx += 1

    return f_labels, f_property_count

# Add data to an issue
def add_properties(issue, parents):
    known_bots = ["Hadoop QA", "Tajo QA", "Hudson", "genericqa", "TezQA", "ASF GitHub Bot"]

    stop = set(stopwords.words('english'))
    
    jira_issue = jira.issue(issue['key'])

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z" # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    created_datetime = datetime.strptime(jira_issue.fields.created, datetime_format)
    if jira_issue.fields.resolutiondate is not None:
        resolved_datetime = datetime.strptime(jira_issue.fields.resolutiondate, datetime_format)
    else:
        resolved_datetime = datetime.now()
        created_datetime = created_datetime.replace(tzinfo=None)

    issue['duration'] = (resolved_datetime - created_datetime).days # days, integer

    issue['status'] = str(jira_issue.fields.status)
    issue['resolution'] = str(jira_issue.fields.resolution)
    issue['hierarchy'] = "None"
    if (str(jira_issue.fields.issuetype) == 'Sub-task'):
        issue['is_a_subtask'] = True
        issue['hierarchy'] = "Child"
        issue['issue_type'] = str(jira_issue.fields.parent.fields.issuetype)
    else:
        issue['is_a_subtask'] = False
        issue['issue_type'] = str(jira_issue.fields.issuetype)
        if issue['key'] in parents:
            issue['hierarchy'] = "Parent"
    if jira_issue.fields.description is not None:
        issue['description_size'] = len([i for i in jira_issue.fields.description.lower().split() if i not in stop])
    else:
        issue['description_size'] = 0
    issue['comment_count'] = 0
    issue['total_comments_size'] = 0
    for comment in jira_issue.fields.comment.comments:
        if comment.author.displayName not in known_bots:
            issue['comment_count'] += 1
            issue['total_comments_size'] += len([i for i in comment.body.lower().split() if i not in stop])
    if issue['comment_count'] != 0:
        issue['average_comment_size'] = issue['total_comments_size']/issue['comment_count']
    else:
        issue['average_comment_size'] = 0
    issue['attachment_count'] = 0
    try:
        for attachment in [str(att) for att in jira_issue.fields.attachment]:
            if ".pdf" in attachment or ".doc" in attachment:
                issue['attachment_count'] += 1
    except:
        print('Issue ' + issue['key'] + ' did not have accessible attachments.')

# Removes the indicator tags and leaves only the actual ADDs
def filter_tags(issues):
    for issue in issues:
        tags_to_delete = []
        for tag in issue['tags']:
            if tag['name'] in ['ANNOTATED', 'BOTTOMUP']:
                tags_to_delete.append(tag)

        for tag in tags_to_delete:
            issue['tags'].remove(tag)
    return issues

# Grab the data that was the output of the analysis script
# And split it up into set intersections
def count_set_overlaps_and_return_sets(AK):
    non = 'non-' if not AK else ''

    # load analysis output
    top_down_AK = filter_tags((json.load(open(f'analysis-output/issues/top-down-{non}AK-issues.json',)))['issues'])
    bottom_up_AK = filter_tags((json.load(open(f'analysis-output/issues/bottom-up-{non}AK.json',)))['issues'])
    maven_AK = filter_tags((json.load(open(f'analysis-output/issues/maven-{non}AK.json')))['issues'])
    bhat_AK = filter_tags((json.load(open(f"analysis-output/issues/bhat-{non}AK.json")))['issues'])

    # separate the three non-bhat (random) sets into a three-way intersection
    td = []
    bu = []
    mav = []
    td_bu = []
    mav_td = []
    mav_bu = []
    all = []

    all_bu_keys = [issue['key'] for issue in bottom_up_AK]
    all_mav_keys = [issue['key'] for issue in maven_AK]
    all_td_keys = [issue['key'] for issue in top_down_AK]

    for issue in maven_AK:
        key = issue['key']
        bu_overlap = key in all_bu_keys
        td_overlap = key in all_td_keys
        if bu_overlap and td_overlap:
            all.append(issue)
        elif bu_overlap:
            mav_bu.append(issue)
        elif td_overlap:
            mav_td.append(issue)
        else:
            mav.append(issue)

    for issue in top_down_AK:
        key = issue['key']
        bu_overlap = key in all_bu_keys
        mav_overlap = key in all_mav_keys
        if bu_overlap and mav_overlap:
            continue
        elif mav_overlap:
            continue
        elif bu_overlap:
            td_bu.append(issue)
        else:
            td.append(issue)
    
    for issue in bottom_up_AK:
        key = issue['key']
        td_overlap = key in all_td_keys
        mav_overlap = key in all_mav_keys
        if td_overlap or mav_overlap:
            continue
        else:
            bu.append(issue)

    # debug output
    output1 = {
        'AK': AK,
        'top-down-only-count': len(td),
        'bottom-up-only-count': len(bu),
        'maven-only-count': len(mav),
        'maven-top-down-count': len(mav_td),
        'maven-bottom-up-count': len(mav_bu),
        'bottom-up-top-down-count': len(td_bu),
        'all-overlap-count': len(all)
    }

    with open(f'analysis-output/issue-sets/{non}AK-issue-set-counts.json', "w") as outfile:
        json.dump(output1, outfile)

    # return result!
    return (td, td_bu, bu, mav, mav_td, mav_bu, all, bhat_AK)


# Add data to all issues in all issue lists
def add_properties_to_issues(AK):
    non = 'non-' if not AK else ''
    td_path = f"analysis-output/issue-sets/{non}AK_td_only.json"
    bu_path = f"analysis-output/issue-sets/{non}AK_bu_only.json"
    mav_path = f"analysis-output/issue-sets/{non}AK_mav_only.json"

    mav_td_path = f"analysis-output/issue-sets/{non}AK_mav_td.json"
    mav_bu_path = f"analysis-output/issue-sets/{non}AK_mav_bu.json"
    td_bu_path = f"analysis-output/issue-sets/{non}AK_td_bu.json"

    all_path = f"analysis-output/issue-sets/{non}AK_all.json"
    bhat_path = f"analysis-output/issue-sets/{non}AK_bhat.json"

    paths = [td_path, bu_path, mav_path, mav_td_path, mav_bu_path, td_bu_path, all_path, bhat_path]
    quit_add = True
    for path in paths:
        if not os.path.exists(path):
            quit_add = False
            break
    if quit_add:
        return

    parents = []
    with open("analysis-output/parents/parents.json", 'r') as f:
        parents = json.load(f)['parents']

    td, td_bu, bu, mav, mav_td, mav_bu, all, bhat = count_set_overlaps_and_return_sets(AK)
    for issue_list in [td, td_bu, bu, mav, mav_td, mav_bu, all, bhat]:
        for issue in issue_list:
            add_properties(issue, parents)
    
    with open(mav_path, "w") as outfile:
        json.dump({'issues': mav}, outfile)
    with open(td_path, "w") as outfile:
        json.dump({'issues': td}, outfile)
    with open(bu_path, "w") as outfile:
        json.dump({'issues': bu}, outfile)
        
    with open(td_bu_path, "w") as outfile:
        json.dump({'issues': td_bu}, outfile)
    with open(mav_td_path, "w") as outfile:
        json.dump({'issues': mav_td}, outfile)
    with open(mav_bu_path, "w") as outfile:
        json.dump({'issues': mav_bu}, outfile)
        
    with open(all_path, "w") as outfile:
        json.dump({'issues': all}, outfile)
    with open(bhat_path, 'w') as outfile:
        json.dump({'issues': bhat}, outfile)

def get_issue_is_parent(issue_key):
    jira_issue = jira.issue(issue_key)
    #if hasattr(jira_issue.fields, 'parent'):
    #    return str(jira_issue.fields.parent)
    #return None
    return len(jira_issue.fields.subtasks) > 0