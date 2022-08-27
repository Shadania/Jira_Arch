import json
from jira import JIRA
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
from nltk import word_tokenize
from nltk.corpus import stopwords
import os

jira = JIRA('https://issues.apache.org/jira')

# Fetches the output from the first script (analysis.py), depending on the argument, which can be either AK or non-AK
def get_issues(AK):
    non = 'non-' if not AK else ''
    top_down_AK = filter_tags((json.load(open(f'analysis-output/top-down-{non}AK-issues.json',)))['issues'])
    bottom_up_all = (json.load(open(f'analysis-output/all-bottom-up-issues.json',)))['issues']
    bottom_up_AK = filter_tags((json.load(open(f'analysis-output/bottom-up-{non}AK.json',)))['issues'])    

    return top_down_AK, bottom_up_all, bottom_up_AK

# Gets the issue sets with saved properties, depending on the argument, which can be either AK or non-AK
def get_AK_issues_with_properties(AK):
    non = 'non-' if not AK else ''
    AK_top_down_only = filter_tags((json.load(open(f'issue-sets/{non}AK_top_down_only.json',)))['issues'])
    AK_intersected = (json.load(open(f'issue-sets/{non}AK_intersected.json',)))['issues']
    AK_bottom_up_only = filter_tags((json.load(open(f'issue-sets/{non}AK_bottom_up_only.json',)))['issues'])    

    return (AK_top_down_only, AK_intersected, AK_bottom_up_only)

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
    top_down_AK, bottom_up_all, bottom_up_AK = get_issues(AK)

    top_down_only = []
    intersected = []
    bottom_up_only = []

    for issue in top_down_AK:
        if issue['key'] in bottom_up_all:
            intersected.append(issue)
        else:
            top_down_only.append(issue)
            
    intersected_keys = [issue['key'] for issue in intersected]
    for issue in bottom_up_AK:
        if issue['key'] not in intersected_keys:
            bottom_up_only.append(issue)

    print(f"Issue sets (Architecutral knowledge: {AK}):")
    print(f"Top down: {len(top_down_only)}", f"Intersected: {len(intersected)}", f"Bottom up: {len(bottom_up_only)}")

    output1 = {
        'AK': AK,
        'top-down-only-count': len(top_down_only),
        'Intersected-count': len(intersected),
        'Bottom-up-count': len(bottom_up_only)
    }

    with open('issue-sets/issue-set-counts.json', "w") as outfile:
        json.dump(output1, outfile)

    return (top_down_only, intersected, bottom_up_only)

# For every issue in top-down, intersected, and bottom-up issue sets, extra properties are added and the issue list is then saved
# Does not do anything if the json files have already been generated before
def add_properties_to_issues(AK):
    non = 'non-' if not AK else ''
    top_down_path = f"issue-sets/{non}AK_top_down_only.json"
    intersected_path = f"issue-sets/{non}AK_intersected.json"
    bottom_up_path = f"issue-sets/{non}AK_bottom_up_only.json"

    if (os.path.exists(top_down_path) and os.path.exists(intersected_path) and os.path.exists(bottom_up_path)):
        return

    top_down_only, intersected, bottom_up_only = count_set_overlaps_and_return_sets(AK)

    i = 0
    print("Adding properties...")
    for issue in top_down_only:
        add_properties(issue)
        print(f"{i}: {issue['key']}")
        i += 1
        
    for issue in intersected:
        add_properties(issue)
        print(f"{i}: {issue['key']}")
        i += 1
        
    for issue in bottom_up_only:
        add_properties(issue)
        print(f"{i}: {issue['key']}")
        i += 1

    output1 = {
        'issues': top_down_only
    }
    output2 = {
        'issues': intersected
    }
    output3 = {
        'issues': bottom_up_only
    }

    non = 'non-' if not AK else ''
    with open(top_down_path, "w") as outfile:
        json.dump(output1, outfile)
    with open(intersected_path, "w") as outfile:
        json.dump(output2, outfile)
    with open(bottom_up_path, "w") as outfile:
        json.dump(output3, outfile)

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
    top_down_AK, _, bottom_up_AK = get_issues(True)
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
    plt.show()

# Plots the approach-indifferent parent data
def plot_parents_2():
    top_down_AK, _, bottom_up_AK = get_issues(True)
    existing_parents, new_parents, new_parents_keys = get_parents_2(top_down_AK, bottom_up_AK)

    labels = ['Classified', 'Not Classified']

    existing = [existing_parents, new_parents]
     
    plt.bar(labels, existing, color='red')
     
    plt.legend()

    plt.title("approach-indifferent parents")

    plt.savefig("figures/Approach-indifferent-parents.jpeg")

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
    for attachment in [str(att) for att in jira_issue.fields.attachment]:
        if ".pdf" in attachment or ".doc" in attachment:
            issue['attachment_count'] += 1

# Large function that honestly does too much... counts how many times different values of a property occur
# breakdown of arguments and what they do:
#   top_down_only, intersected, bottom_up_only: The issue sets
#   issue_property: The property to count
#   static labels: A list of specific labels to use
#   cutoff: The fraction of the maximum value to allow to count towards. Values below this are deemed insignificant
#   raw_count: If true, the values returned are not in percentages, but the actual property count
def count_property(top_down_only, intersected, bottom_up_only, issue_property, static_labels = [], cutoff = 0.05, raw_count = False):
    labels = set()
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

    labels = list(labels)

    top_down_only_property_count = []
    intersected_property_count = []
    bottom_up_only_property_count = []

    if static_labels:
        for label in static_labels:
            top_down_only_property_count.append((top_down_only_properties.get(label, 0)/(1 if raw_count else len(top_down_only)*100)))
            intersected_property_count.append((intersected_properties.get(label, 0)/(1 if raw_count else len(intersected)*100)))
            bottom_up_only_property_count.append((bottom_up_only_properties.get(label, 0)/(1 if raw_count else len(bottom_up_only)*100)))
        return labels, top_down_only_property_count, intersected_property_count, bottom_up_only_property_count
    
    for label in labels:
        top_down_only_property_count.append((top_down_only_properties.get(label, 0)/(1 if raw_count else len(top_down_only)*100)))
        intersected_property_count.append((intersected_properties.get(label, 0)/(1 if raw_count else len(intersected)*100)))
        bottom_up_only_property_count.append((bottom_up_only_properties.get(label, 0)/(1 if raw_count else len(bottom_up_only)*100)))

    max_value = max(top_down_only_property_count + intersected_property_count + bottom_up_only_property_count)

    f_labels = []

    f_top_down_only_property_count = []
    f_intersected_property_count = []
    f_bottom_up_only_property_count = []

    for i in range(len(labels)):
        if max((top_down_only_property_count[i], intersected_property_count[i], bottom_up_only_property_count[i])) > cutoff*max_value:
            f_labels.append(labels[i])
            f_top_down_only_property_count.append(top_down_only_property_count[i])
            f_intersected_property_count.append(intersected_property_count[i])
            f_bottom_up_only_property_count.append(bottom_up_only_property_count[i])

    return f_labels, f_top_down_only_property_count, f_intersected_property_count, f_bottom_up_only_property_count

# Plots a multi-bar chart (A color for each issue set) for values of a property. 
def plot_property_comparison(top_down_only, intersected, bottom_up_only, issue_property):
    labels, top_down_property, intersected_property, bottom_up_property = count_property(top_down_only, intersected, bottom_up_only, issue_property)

    barWidth = 0.25

    r1 = range(len(labels))
    r2 = [x + barWidth for x in r1]
    r3 = [x + barWidth for x in r2]
     
    plt.bar(r1, top_down_property, color='red', width=barWidth, edgecolor='white', label='Top Down')
    plt.bar(r2, intersected_property, color='blue', width=barWidth, edgecolor='white', label='Intersected')
    plt.bar(r3, bottom_up_property, color='green', width=barWidth, edgecolor='white', label='Bottom Up')
     
    plt.title(f"Property '{issue_property}'")
    plt.ylabel("%")
    plt.xticks([r + barWidth for r in range(len(labels))], labels)

    plt.legend()
    plt.savefig(f"figures/property_'{issue_property}'.png")

    plt.show()

# Gets the data that compares AK vs non-AK issues for a specific property
def get_AK_issue_VS_data(top_down_only, intersected, bottom_up_only, issue_property, labels = []):
    labels, top_down_property, intersected_property, bottom_up_property = count_property(top_down_only, intersected, bottom_up_only, issue_property, labels, 0.05, True)
    issues = [((x + y + z)/(len(top_down_only) + len(intersected) + len(bottom_up_only)))*100 for x,y,z in zip(top_down_property, intersected_property, bottom_up_property)]

    # with open('output.json', 'w+') as f:
    #     json.dump(issues, f)

    return labels, issues

# plots a stacked barchart comparison of AK and non-AK issue for a specific property
def plot_AK_vs_non_AK(property):
    AK_top_down_only, AK_intersected, AK_bottom_up_only = get_AK_issues_with_properties(True)
    non_AK_top_down_only, non_AK_intersected, non_AK_bottom_up_only = get_AK_issues_with_properties(False)
    AK_labels, AK_issue_counts = get_AK_issue_VS_data(AK_top_down_only, AK_intersected, AK_bottom_up_only, property)
    _, non_AK_issue_counts = get_AK_issue_VS_data(non_AK_top_down_only, non_AK_intersected, non_AK_bottom_up_only, property, AK_labels)

    x_labels = ['AK Issues', 'Non-AK Issues']

    fig, ax = plt.subplots()

    for i in range(len(AK_labels)):
        ax.bar(x_labels, [AK_issue_counts[i], non_AK_issue_counts[i]], 0.7, bottom = [sum(AK_issue_counts[:i]), sum(non_AK_issue_counts[:i])], label=AK_labels[i])
    ax.legend()

    plt.title(f"Property '{property}'")

    plt.savefig(f'figures/AK_vs_non_AK_{property}.png')
    plt.show()

# For some properties, a box plot is more suitable
def box_plot_property_distribution(top_down_only, intersected, bottom_up_only, issue_property):
    top_down_only_values = [issue[issue_property] for issue in top_down_only]
    intersected_values = [issue[issue_property] for issue in intersected]
    bottom_up_only_values = [issue[issue_property] for issue in bottom_up_only]

    data = [top_down_only_values, intersected_values, bottom_up_only_values]

    fig, ax = plt.subplots()

    ax.boxplot(data)

    plt.xticks([1, 2, 3], ["Top Down", "Intersected", "Bottom Up"])

    plt.title(f"property '{issue_property}'")

    plt.savefig(f"figures/property_'{issue_property}'_box.png")
     
    plt.show()

# Box plot comparing AK and non AK issues for a specific property
def box_plot_AK_vs_non_AK(property):
    AK_top_down_only, AK_intersected, AK_bottom_up_only = get_AK_issues_with_properties(True)
    non_AK_top_down_only, non_AK_intersected, non_AK_bottom_up_only = get_AK_issues_with_properties(False)

    AK_values = [issue[property] for issue in AK_top_down_only + AK_intersected + AK_bottom_up_only ]
    non_AK_values = [issue[property] for issue in non_AK_top_down_only + non_AK_intersected + non_AK_bottom_up_only]

    data = [AK_values, non_AK_values]

    fig, ax = plt.subplots()

    ax.boxplot(data)

    plt.xticks([1, 2], ["AK Issues", "Non-AK Issues"])

    plt.title(f"property '{property}'")

    plt.savefig(f"figures/property_'{property}'_box_AK_vs_non-AK.png")
     
    plt.show()
        
# All the AK issue property comparisons are called here
def plot_comparisons(AK):
    AK_top_down_only, AK_intersected, AK_bottom_up_only = get_AK_issues_with_properties(AK)
    plot_property_comparison(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'status')
    plot_property_comparison(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'resolution')
    plot_property_comparison(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'is_a_subtask')
    plot_property_comparison(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'issue_type')
    box_plot_property_distribution(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'description_size')
    box_plot_property_distribution(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'comment_count')
    box_plot_property_distribution(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'average_comment_size')
    box_plot_property_distribution(AK_top_down_only, AK_intersected, AK_bottom_up_only, 'attachment_count')

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
plot_comparisons(AK)
add_properties_to_issues(not AK)
AK_vs_non_AK()
parents()


