import json
from jira import JIRA
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
from nltk import word_tokenize
from nltk.corpus import stopwords
import os

jira = JIRA('https://issues.apache.org/jira')
show_figures = False

# Fetches the output from the first script (analysis.py), depending on the argument, which can be either AK or non-AK
def get_issues(AK):
    non = 'non-' if not AK else ''
    top_down_AK = filter_tags((json.load(open(f'analysis-output/top-down-{non}AK-issues.json',)))['issues'])
    bottom_up_all = (json.load(open(f'analysis-output/all-bottom-up-issues.json',))['issues'])
    bottom_up_AK = filter_tags((json.load(open(f'analysis-output/bottom-up-{non}AK.json',)))['issues'])
    maven_AK = filter_tags((json.load(open(f'analysis-output/maven-{non}AK.json')))['issues'])
    bhat_AK = filter_tags((json.load(open(f"analysis-output/bhat-{non}AK.json")))['issues'])

    return top_down_AK, bottom_up_all, bottom_up_AK, maven_AK, bhat_AK

# Gets the issue sets with saved properties, depending on the argument, which can be either AK or non-AK
def get_AK_issues_with_properties(AK):
    non = 'non-' if not AK else ''
    td_path = f"issue-sets/{non}AK_td_only.json"
    bu_path = f"issue-sets/{non}AK_bu_only.json"
    mav_path = f"issue-sets/{non}AK_mav_only.json"

    mav_td_path = f"issue-sets/{non}AK_mav_td.json"
    mav_bu_path = f"issue-sets/{non}AK_mav_bu.json"
    td_bu_path = f"issue-sets/{non}AK_td_bu.json"

    all_path = f"issue-sets/{non}AK_all.json"

    bhat_path = f"issue-sets/{non}AK_bhat.json"

    td = filter_tags((json.load(open(td_path)))['issues'])
    bu = filter_tags((json.load(open(bu_path)))['issues'])
    mav = filter_tags((json.load(open(mav_path)))['issues'])

    td_bu = filter_tags((json.load(open(td_bu_path)))['issues'])
    mav_td = filter_tags((json.load(open(mav_td_path)))['issues'])
    mav_bu = filter_tags((json.load(open(mav_bu_path)))['issues'])
    
    all = filter_tags((json.load(open(all_path)))['issues'])
    bhat = filter_tags((json.load(open(bhat_path)))['issues'])

    return (td, bu, mav, mav_td, mav_bu, td_bu, all, bhat)

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

# Creates three sets of issues:
#     Top down only
#     Intersected (present in both top down and bottom up)
#     Bottom-up only
def count_set_overlaps_and_return_sets(AK):
    top_down_AK, bottom_up_all, bottom_up_AK, maven_AK, bhat_AK = get_issues(AK)

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

    #print(f"Issue sets (Architecutral knowledge: {AK}):")
    #print(f"Top down: {len(td)}", f"Intersected: {len(td_bu)}", f"Bottom up: {len(bu)}")

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

    with open('issue-sets/issue-set-counts.json', "w") as outfile:
        json.dump(output1, outfile)

    return (td, td_bu, bu, mav, mav_td, mav_bu, all, bhat_AK)

# For every issue in top-down, intersected, and bottom-up issue sets, extra properties are added and the issue list is then saved
# Does not do anything if the json files have already been generated before
def add_properties_to_issues(AK):
    non = 'non-' if not AK else ''
    td_path = f"issue-sets/{non}AK_td_only.json"
    bu_path = f"issue-sets/{non}AK_bu_only.json"
    mav_path = f"issue-sets/{non}AK_mav_only.json"

    mav_td_path = f"issue-sets/{non}AK_mav_td.json"
    mav_bu_path = f"issue-sets/{non}AK_mav_bu.json"
    td_bu_path = f"issue-sets/{non}AK_td_bu.json"

    all_path = f"issue-sets/{non}AK_all.json"
    bhat_path = f"issue-sets/{non}AK_bhat.json"

    paths = [td_path, bu_path, mav_path, mav_td_path, mav_bu_path, td_bu_path, all_path, bhat_path]
    quit_add = True
    for path in paths:
        if not os.path.exists(path):
            quit_add = False
            break
    if quit_add:
        return

    td, td_bu, bu, mav, mav_td, mav_bu, all, bhat = count_set_overlaps_and_return_sets(AK)

    tupled = (td, td_bu, bu, mav, mav_td, mav_bu, all, bhat)
    i = 0
    for issue_list in tupled:
        print('done ' + str(i) + ' issues')
        for issue in issue_list:
            add_properties(issue)
            i += 1
            # print(f"{i}: {issue['key']}")
    print('done, dumping json')

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
    print('done')

# Gets existing and new parent counts for top down and bottom up separately. Fetches from JSON directly if it already exists.
def get_parents(top_down, bottom_up):
    parents_path = f'parents/approach-specific-parents.json'

    if (os.path.exists(parents_path)):
        parents = json.load(open(parents_path))
        return parents['top_down_existing_parents'], parents['bottom_up_existing_parents'], parents['top_down_new_parents'], parents['bottom_up_new_parents']

    top_down_keys = [issue['key'] for issue in top_down]
    bottom_up_keys = [issue['key'] for issue in bottom_up]
    top_down_existing_parents = set()
    bottom_up_existing_parents = set()
    top_down_new_parents = set()
    bottom_up_new_parents = set()

    for key in top_down_keys:
        jira_issue = jira.issue(key)
        if hasattr(jira_issue.fields, 'parent'):
            parent_key = str(jira_issue.fields.parent)
            print("Parent found: " + parent_key)
            if parent_key in top_down_keys:
                top_down_existing_parents.add(parent_key)
            else:
                top_down_new_parents.add(parent_key)

    for key in bottom_up_keys:
        jira_issue = jira.issue(key)
        if hasattr(jira_issue.fields, 'parent'):
            parent_key = str(jira_issue.fields.parent)
            print("Parent found: " + parent_key)
            if parent_key in bottom_up_keys:
                bottom_up_existing_parents.add(parent_key)
            else:
                bottom_up_new_parents.add(parent_key)

    output = {
        'top_down_existing_parents': len(top_down_existing_parents),
        'bottom_up_existing_parents': len(bottom_up_existing_parents),
        'top_down_new_parents': len(top_down_new_parents),
        'bottom_up_new_parents': len(bottom_up_new_parents)
    }

    with open(parents_path, "w") as outfile:
        json.dump(output, outfile)

    return (len(top_down_existing_parents), len(bottom_up_existing_parents), len(top_down_new_parents), len(bottom_up_new_parents))

# Gets existing and new parent counts regardless of approach used. Fetches from JSON directly if it already exists.
def get_parents_2(top_down, bottom_up):
    parents_path = f'parents/general-parents.json'
    non_classified_list_path = f'parents/Non-classified-parents.json'

    if (os.path.exists(parents_path) and os.path.exists(non_classified_list_path)):
        parents = json.load(open(parents_path))
        parents_list = json.load(open(non_classified_list_path))
        return parents['existing_parents'], parents['new_parents'], parents_list['issues']

    top_down_keys = [issue['key'] for issue in top_down]
    bottom_up_keys = [issue['key'] for issue in bottom_up]
    all_keys = top_down_keys + bottom_up_keys
    existing_parents = set()
    new_parents = set()

    for key in all_keys:
        jira_issue = jira.issue(key)
        if hasattr(jira_issue.fields, 'parent'):
            parent_key = str(jira_issue.fields.parent)
            print("Parent found: " + parent_key)
            if parent_key in all_keys:
                existing_parents.add(parent_key)
            else:
                new_parents.add(parent_key)

    output1 = {
        'issues': list(new_parents)
    }
    output2 = {
        'existing_parents': len(existing_parents),
        'new_parents': len(new_parents)
    }
    with open(non_classified_list_path, "w") as outfile:
        json.dump(output1, outfile)
    with open(parents_path, "w") as outfile:
        json.dump(output2, outfile)

    return len(existing_parents), len(new_parents), new_parents

# Plots the approach-specific parent data
def plot_parents():
    top_down_AK, _, bottom_up_AK, maven_AK, bhat_AK = get_issues(True)
    top_down_existing_parents, bottom_up_existing_parents, top_down_new_parents, bottom_up_new_parents = get_parents(top_down_AK, bottom_up_AK)

    labels = ['Top Down', 'Bottom Up']

    existing = [top_down_existing_parents, bottom_up_existing_parents]
    new = [top_down_new_parents, bottom_up_new_parents]

    barWidth = 0.33

    r1 = range(len(labels))
    r2 = [x + barWidth for x in r1]
     
    plt.bar(r1, existing, color='red', width=barWidth, edgecolor='white', label='Classified')
    plt.bar(r2, new, color='blue', width=barWidth, edgecolor='white', label='Not Classified')
     
    plt.xticks([r + barWidth/2 for r in range(len(labels))], labels)

    plt.title(f"Approach-specific parents")

    plt.legend()

    plt.savefig("figures/Approach-specific-parents.jpeg")
    if show_figures:
        plt.show()

# Plots the approach-indifferent parent data
def plot_parents_2():
    top_down_AK, _, bottom_up_AK, maven_AK, bhat_AK = get_issues(True)
    existing_parents, new_parents, new_parents_keys = get_parents_2(top_down_AK, bottom_up_AK)

    labels = ['Classified', 'Not Classified']

    existing = [existing_parents, new_parents]
     
    plt.bar(labels, existing, color='red')
     
    plt.legend()

    plt.title("approach-indifferent parents")

    plt.savefig("figures/Approach-indifferent-parents.jpeg")

    if show_figures:
        plt.show()

# Adds extra properties to issues. These are either values from direct fields or derived from them.  
def add_properties(issue):
    known_bots = ["Hadoop QA", "Tajo QA", "Hudson", "genericqa", "TezQA", "ASF GitHub Bot"]

    stop = set(stopwords.words('english'))
    
    jira_issue = jira.issue(issue['key'])
    issue['status'] = str(jira_issue.fields.status)
    issue['resolution'] = str(jira_issue.fields.resolution)
    if (str(jira_issue.fields.issuetype) == 'Sub-task'):
        issue['is_a_subtask'] = True
        issue['issue_type'] = str(jira_issue.fields.parent.fields.issuetype)
    else:
        issue['is_a_subtask'] = False
        issue['issue_type'] = str(jira_issue.fields.issuetype)
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

# Large function that honestly does too much... counts how many times different values of a property occur
# breakdown of arguments and what they do:
#   top_down_only, intersected, bottom_up_only: The issue sets
#   issue_property: The property to count
#   static labels: A list of specific labels to use
#   cutoff: The fraction of the maximum value to allow to count towards. Values below this are deemed insignificant
#   raw_count: If true, the values returned are not in percentages, but the actual property count
def count_property(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, issue_property, static_labels = [], cutoff = 0.05, raw_count = False):
    labels = set()

    properties = []
    issue_lists = [td, bu, mav, mav_td, mav_bu, td_bu, all, bhat]
    idx = 0
    for issue_list in issue_lists:
        properties.append({})
        for issue in issue_list:
            val = issue[issue_property]
            if val not in properties[idx]:
                properties[idx][val] = 0
            properties[idx][val] += 1
            labels.add(val)
        idx += 1

    """
    top_down_only_properties = {}
    for issue in top_down_only:
        if issue[issue_property] not in top_down_only_properties:
            top_down_only_properties[issue[issue_property]] = 0
        top_down_only_properties[issue[issue_property]] += 1
        labels.add(issue[issue_property])
        
    intersected_properties = {}
    for issue in intersected:
        if issue[issue_property] not in intersected_properties:
            intersected_properties[issue[issue_property]] = 0
        intersected_properties[issue[issue_property]] += 1
        labels.add(issue[issue_property])
        
    bottom_up_only_properties = {}
    for issue in bottom_up_only:
        if issue[issue_property] not in bottom_up_only_properties:
            bottom_up_only_properties[issue[issue_property]] = 0
        bottom_up_only_properties[issue[issue_property]] += 1
        labels.add(issue[issue_property])
    """

    labels = list(labels)


    property_count = []
    for issue_list in issue_lists:
        property_count.append([])
    idx = 0
    if static_labels:
        for label in static_labels:
            for issue_list in issue_lists:
                property_count[idx].append((properties[idx].get(label, 0)/(1 if raw_count else len(issue_list)*100)))
            idx += 1
        return labels, property_count[0], property_count[1], property_count[2], property_count[3], property_count[4], property_count[5], property_count[6], property_count[7]


    """
    top_down_only_property_count = []
    intersected_property_count = []
    bottom_up_only_property_count = []
    if static_labels:
        for label in static_labels:
            top_down_only_property_count.append((top_down_only_properties.get(label, 0)/(1 if raw_count else len(top_down_only)*100)))
            intersected_property_count.append((intersected_properties.get(label, 0)/(1 if raw_count else len(intersected)*100)))
            bottom_up_only_property_count.append((bottom_up_only_properties.get(label, 0)/(1 if raw_count else len(bottom_up_only)*100)))
        return labels, top_down_only_property_count, intersected_property_count, bottom_up_only_property_count
    """


    for label in labels:
        idx = 0
        for issue_list in issue_lists:
            # list.append((properties[idx].get(label, 0)/(1 if raw_count else len(issue_lists[idx]))))
            property_count[idx].append((properties[idx].get(label, 0)/(1 if raw_count else len(issue_list)*100)))
            idx += 1

    """
    for label in labels:
        top_down_only_property_count.append((top_down_only_properties.get(label, 0)/(1 if raw_count else len(top_down_only)*100)))
        intersected_property_count.append((intersected_properties.get(label, 0)/(1 if raw_count else len(intersected)*100)))
        bottom_up_only_property_count.append((bottom_up_only_properties.get(label, 0)/(1 if raw_count else len(bottom_up_only)*100)))
    """

    property_count_all = []
    for issue_list in property_count:
        property_count_all += issue_list
    max_value = max(property_count_all)

    # max_value = max(top_down_only_property_count + intersected_property_count + bottom_up_only_property_count)

    # new addition!
    # due to some of bhat's data not being 100% available anymore for some reason
    # the property_count will be zero-filled
    max_len = len(labels)
    #for issue_list in property_count:
    #    if len(issue_list) > max_len:
    #        max_len = len(issue_list)
    for issue_list in property_count:
        while len(issue_list) < max_len:
            issue_list.append(0.0)

    f_labels = []

    f_property_count = []
    for issue_list in issue_lists:
        f_property_count.append([])
    for i in range(len(labels)):
        #print(property_count)
        #print(issue_property)
        #print(labels[i])
        #print(i)
        tupled = (property_count[0][i], property_count[1][i], property_count[2][i], property_count[3][i], property_count[4][i], property_count[5][i], property_count[6][i], property_count[7][i])
        if max(tupled) > cutoff*max_value:
            f_labels.append(labels[i])
            idx = 0
            for issue_list in issue_lists:
                #print(f_property_count)
                f_property_count[idx].append(property_count[idx][i])
                idx += 1


    """
    f_top_down_only_property_count = []
    f_intersected_property_count = []
    f_bottom_up_only_property_count = []

    for i in range(len(labels)):
        if max((top_down_only_property_count[i], intersected_property_count[i], bottom_up_only_property_count[i])) > cutoff*max_value:
            f_labels.append(labels[i])
            f_top_down_only_property_count.append(top_down_only_property_count[i])
            f_intersected_property_count.append(intersected_property_count[i])
            f_bottom_up_only_property_count.append(bottom_up_only_property_count[i])
    """


    return f_labels, f_property_count[0], f_property_count[1], f_property_count[2], f_property_count[3], f_property_count[4], f_property_count[5], f_property_count[6], f_property_count[7]

# Plots a multi-bar chart (A color for each issue set) for values of a property. 
def plot_property_comparison(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, issue_property):
    labels, prop_td, prop_bu, prop_mav, prop_mav_td, prop_mav_bu, prop_td_bu, prop_all, prop_bhat = count_property(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, issue_property)

    barWidth = 0.25

    r1 = range(len(labels))
    r2 = [x + barWidth for x in r1]
    r3 = [x + barWidth for x in r2]
    
    plt.bar(r1, prop_td, color='red', width=barWidth, edgecolor='white', label='Top Down')
    plt.bar(r2, prop_bu, color = 'blue', width=barWidth, edgecolor='white', label='Bottom Up')
    plt.bar(r3, prop_mav, color = 'yellow', width=barWidth, edgecolor='white', label='Maven')
    
    plt.bar(r1, prop_mav_td, color = 'orange', width=barWidth, edgecolor='white', label='Maven & Top Down')
    plt.bar(r2, prop_mav_bu, color='green', width=barWidth, edgecolor='white', label='Maven & Bottom Up')
    plt.bar(r3, prop_td_bu, color='purple', width=barWidth, edgecolor='white', label='Top Down & Bottom Up')
    
    plt.bar(r2, prop_all, color='lightgrey', width=barWidth, edgecolor='white', label='Full Overlap')
    plt.bar(r3, prop_bhat, color='black', width=barWidth, edgecolor='white', label='Random')
     
    plt.title(f"Property '{issue_property}'")
    plt.ylabel("%")
    plt.xticks([r + barWidth for r in range(len(labels))], labels)

    plt.legend()
    plt.savefig(f"figures/property_'{issue_property}'.png")

    if show_figures:
        plt.show()

# Gets the data that compares AK vs non-AK issues for a specific property
def get_AK_issue_VS_data(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, issue_property, labels = []):
    labels, prop_td, prop_bu, prop_mav, prop_mav_td, prop_mav_bu, prop_td_bu, prop_all, prop_bhat = count_property(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, issue_property, labels, 0.05, True)
    issue_lists = [td, bu, mav, mav_td, mav_bu, td_bu, all, bhat]

    total_len = 0
    for list in issue_lists:
        total_len += len(list)

    print('aaaa')
    print([prop_td, prop_bu, prop_mav, prop_mav_td, prop_mav_bu, prop_td_bu, prop_all, prop_bhat])
    # print([td, bu, mav, mav_td, mav_bu, td_bu, all, bhat])

    # issues = [((x + y + z)/(total_len))*100 for x,y,z in zip(top_down_property, intersected_property, bottom_up_property)]
    issues = [((a+b+c+d+e+f+g+h)/(total_len))*100 for a,b,c,d,e,f,g,h in zip(prop_td, prop_bu, prop_mav, prop_mav_td, prop_mav_bu, prop_td_bu, prop_all, prop_bhat)]

    return labels, issues

# plots a stacked barchart comparison of AK and non-AK issue for a specific property
def plot_AK_vs_non_AK(property):
    td, bu, mav, mav_td, mav_bu, td_bu, all, bhat = get_AK_issues_with_properties(True)
    non_td, non_bu, non_mav, non_mav_td, non_mav_bu, non_td_bu, non_all, non_bhat = get_AK_issues_with_properties(False)
    AK_labels, AK_issue_counts = get_AK_issue_VS_data(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, property)
    _, non_AK_issue_counts = get_AK_issue_VS_data(non_td, non_bu, non_mav, non_mav_td, non_mav_bu, non_td_bu, non_all, non_bhat, property, AK_labels)

    x_labels = ['AK Issues', 'Non-AK Issues']

    fig, ax = plt.subplots()

    # normalize data so it's usable
    while len(AK_issue_counts) < len(AK_labels):
        AK_issue_counts.append(0.0)
    while len(non_AK_issue_counts) < len(AK_labels):
        non_AK_issue_counts.append(0.0)

    for i in range(len(AK_labels)):
        print(AK_issue_counts)
        print(non_AK_issue_counts)
        print(i)
        print(len(AK_labels))
        print(AK_labels[i])
        print(property)
        height = [AK_issue_counts[i], non_AK_issue_counts[i]]
        bottom = [sum(AK_issue_counts[:i]), sum(non_AK_issue_counts[:i])]
        ax.bar(x_labels, height, 0.7, bottom = bottom, label=AK_labels[i])
    ax.legend()

    plt.title(f"Property '{property}'")

    plt.savefig(f'figures/AK_vs_non_AK_{property}.png')
    if show_figures:
        plt.show()

# For some properties, a box plot is more suitable
def box_plot_property_distribution(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, issue_property):
    
    values = []
    for list in [td, bu, mav, mav_td, mav_bu, td_bu, all, bhat]:
        values.append([issue[issue_property] for issue in list])
        # values.append(list.values())


    #top_down_only_values = [issue[issue_property] for issue in top_down_only]
    #intersected_values = [issue[issue_property] for issue in intersected]
    #bottom_up_only_values = [issue[issue_property] for issue in bottom_up_only]

    # data = [top_down_only_values, intersected_values, bottom_up_only_values]

    fig, ax = plt.subplots()

    ax.boxplot(values)

    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8], ['TD', 'BU', 'MAV', 'MAV-TD', 'MAV-BU', 'TD-BU', 'ALL', 'RANDOM'])

    plt.title(f"property '{issue_property}'")

    plt.savefig(f"figures/property_'{issue_property}'_box.png")
     
    if show_figures:
        plt.show()

# Box plot comparing AK and non AK issues for a specific property
def box_plot_AK_vs_non_AK(property):
    td, bu, mav, mav_td, mav_bu, td_bu, all, bhat = get_AK_issues_with_properties(True)
    non_td, non_bu, non_mav, non_mav_td, non_mav_bu, non_td_bu, non_all, non_bhat = get_AK_issues_with_properties(False)

    ak_values_list = []
    for list in [td, bu, mav, mav_td, mav_bu, td_bu, all, bhat]:
        ak_values_list += list
    non_ak_values_list = []
    for list in [non_td, non_bu, non_mav, non_mav_td, non_mav_bu, non_td_bu, non_all, non_bhat]:
        non_ak_values_list += list

    AK_values = [issue[property] for issue in ak_values_list]
    non_AK_values = [issue[property] for issue in non_ak_values_list]

    data = [AK_values, non_AK_values]

    fig, ax = plt.subplots()

    ax.boxplot(data)

    plt.xticks([1, 2], ["AK Issues", "Non-AK Issues"])

    plt.title(f"property '{property}'")

    plt.savefig(f"figures/property_'{property}'_box_AK_vs_non-AK.png")
     
    if show_figures:
        plt.show()
        
# All the AK issue property comparisons are called here
def plot_comparisons(AK):
    td, bu, mav, mav_td, mav_bu, td_bu, all, bhat = get_AK_issues_with_properties(AK)
    print('a')
    plot_property_comparison(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'status')
    print('b')
    plot_property_comparison(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'resolution')
    print('c')
    plot_property_comparison(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'is_a_subtask')
    print('d')
    plot_property_comparison(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'issue_type')
    print('e')
    box_plot_property_distribution(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'description_size')
    print('f')
    box_plot_property_distribution(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'comment_count')
    print('g')
    box_plot_property_distribution(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'average_comment_size')
    print('h')
    box_plot_property_distribution(td, bu, mav, mav_td, mav_bu, td_bu, all, bhat, 'attachment_count')

# All the AK vs non-AK issue property comparisons are called here
def AK_vs_non_AK():
    plot_AK_vs_non_AK('status')
    plot_AK_vs_non_AK('resolution')
    plot_AK_vs_non_AK('is_a_subtask')
    plot_AK_vs_non_AK('issue_type')
    box_plot_AK_vs_non_AK('description_size')
    box_plot_AK_vs_non_AK('comment_count')
    box_plot_AK_vs_non_AK('average_comment_size')
    box_plot_AK_vs_non_AK('attachment_count')

def parents():
    plot_parents()
    plot_parents_2()

AK = True
add_properties_to_issues(AK)
print("step 2")
plot_comparisons(AK)
print("step 3")
add_properties_to_issues(not AK)
print("step 4")
AK_vs_non_AK()
print("step 5")
parents()


