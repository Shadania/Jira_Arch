# required package
import nltk

# apply data/changed_issues.csv to bottomup & topdown
# not maven because that was after the changes were made
# not bhat because that wasn't checked anyway
changed_issues = {}
with open('data/changed_issues.csv') as f:
    for line in f:
        lineSplit = [x for x in line.strip().split(',') if x]
        key = lineSplit[0]
        changed_issues[key] = []
        for tag in lineSplit[1:]:
            changed_issues[key].append(tag)

# bottomup
import pandas
def do_bottomup():
    bottomup_path = "data/bottomup/bottom-up-saved.xlsx"
    bottomup = pandas.ExcelFile(bottomup_path)
    sheet = bottomup.parse(1)

    headers=['Existence', 'Property', 'Executive']

    for index, row in sheet.iterrows():
        key = row['issue_id']
        if not key in changed_issues:
            continue

        types = []
        for header in headers:
            toWrite = 'x' if (header in changed_issues[key]) else float('nan')
            row[header] = toWrite

    sheets = {
        "Sheet1": bottomup.parse(0),
        "Sheet2": sheet,
        "Sheet3": bottomup.parse(2)
    }

    writer = pandas.ExcelWriter(bottomup_path, engine='xlsxwriter')

    for sheet_name in sheets:
        sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)

    writer.save()

# topdown
import json
def do_topdown():
    CAC_path = 'data/topdown/ComponentsAndConnectors.json'
    DF_path = 'data/topdown/DecisionFactors.json'
    R_path = 'data/topdown/Rationale.json'
    RS_path = 'data/topdown/ReusableSolutions.json'

    for file_path in [CAC_path, DF_path, R_path, RS_path]:
        issue_list = None
        with open(file_path, 'r') as f:
            issue_list = json.load(f)
        for line in issue_list['issues']: # {'key': ..., 'tags': [{'name': ...}]}
            key = line['key']
            if key not in changed_issues:
                continue
            
            tags = ['Existence', 'Property', 'Executive']
            # remove any type tags
            newTags = [x for x in line['tags'] if x not in tags]
            # add the correct ones back
            for tag in changed_issues[key]:
                newTags.append({'name':tag})
            # write
            line['tags'] = newTags

        # write
        with open(file_path, 'w') as f:
            json.dump(issue_list, f)


# leaving this in so that it can be used in the future on new data
# or the logic reused for similar enough data
def prepare():
    nltk.download('stopwords')
    do_bottomup()
    do_topdown()

if __name__ == '__main__':
    prepare()