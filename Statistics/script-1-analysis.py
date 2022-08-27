import json
import os

from script_shared import add_properties_to_issues, count_set_overlaps_and_return_sets, get_issue_is_parent
from script_shared import annotated, bottomup
from script_shared import get_top_down_issues, get_maven_issues, get_bottom_up_issues



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
    with open(f"analysis-output/issues/top-down-{non}AK-issues.json", "w") as outfile:
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
    with open(f"analysis-output/issues/bottom-up-{non}AK.json", "w") as outfile:
        json.dump(output, outfile)

def make_maven_issues_json(AK):
    issues = get_maven_issues()[3] # 'total' statistic
    output_issues = []
    for issue in issues:
        if (len(issue['tags']) > 0) == AK:
            output_issues.append(issue)

    non = 'non-' if not AK else ''
    with open(f"analysis-output/issues/maven-{non}AK.json", 'w+') as outfile:
        json.dump({'issues': output_issues}, outfile)

def make_bhat_issues_json(AK):
    issues = []
    first = True
    with open('data/bhat/bhat_labels.csv') as f:
        for line in f:
            if first:
                first = False
                continue
            fields = line.strip().split(',')
            if (fields[1] == "True") == AK:
                key = fields[0]
                tags = []
                if fields[2] in ['Behavioral decision', 'Structural decision', 'Non-existence - ban decision']:
                    tags.append({'name': 'Existence'})
                elif fields[2] != 'N/A':
                    tags.append({'name': fields[2]})
                issues.append({'key': key, 'tags': tags})
    non = 'non-' if not AK else ''
    with open(f"analysis-output/issues/bhat-{non}AK.json", 'w+') as outfile:
        json.dump({'issues': issues}, outfile)

def find_parents():
    # check if we've done this before
    parents_path = f'analysis-output/parents/parents.json'
    if (os.path.exists(parents_path)):
        parents = json.load(open(parents_path))
        return parents

    # get all concerned issue keys
    sets_AK = count_set_overlaps_and_return_sets(True)
    sets_non_AK = count_set_overlaps_and_return_sets(False)

    issue_keys = []
    for issue_set in sets_AK + sets_non_AK:
        for issue in issue_set:
            issue_keys.append(issue['key'])

    issue_parents = set()

    for key in issue_keys:
        if get_issue_is_parent(key):
            issue_parents.add(key)

    with open(parents_path, 'w+') as f:
        json.dump({'parents': list(issue_parents)}, f)

# Generate issue data
for val in [True, False]:
    make_maven_issues_json(val)
    make_bhat_issues_json(val)
    make_top_down_issues_json(val)
    make_bottom_up_issues_json(val)

find_parents()
count_set_overlaps_and_return_sets(True)
count_set_overlaps_and_return_sets(False)
add_properties_to_issues(True)
add_properties_to_issues(False)