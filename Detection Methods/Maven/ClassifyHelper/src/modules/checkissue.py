import pandas as pd
import cmds
import res

class data:
	issues_dic = None

@cmds.CMD("Check if an issue is in the IssuesDataset", "check")
def checkIssue(msg):
	if data.issues_dic == None:
		classified_str = 'Classified architectural issues'
		nonarch_str = 'Classified non-architectural'
		nonClass_str = 'Non-classified issues'
		annotated_str = 'AnotatedIssuesNotClassified'
		
		engine = 'openpyxl'
		
		classified = pd.read_excel(res.getFileName('resources/IssuesDataset.xlsx'), sheet_name=classified_str, engine=engine)
		nonarch = pd.read_excel(res.getFileName('resources/IssuesDataset.xlsx'), sheet_name=nonarch_str, engine=engine)
		nonClass = pd.read_excel(res.getFileName('resources/IssuesDataset.xlsx'), sheet_name=nonClass_str, engine=engine)
		annotated = pd.read_excel(res.getFileName('resources/IssuesDataset.xlsx'), sheet_name=annotated_str, engine=engine)
		data.issues_dic = {
			classified_str: {},
			nonarch_str: {},
			nonClass_str: {},
			annotated_str: {}
		}

		for col in classified.iloc:
			details = []
			for type in ['Type1', 'Type2', 'Type3']:
				if col[type]:
					details.append(col[type])
			data.issues_dic[classified_str][col['issues key']] = details

		for col in nonarch.iloc:
			data.issues_dic[nonarch_str][col['issues key']] = []

		for col in nonClass.iloc:
			data.issues_dic[nonClass_str][col['Issue key']] = []

		for col in annotated.iloc:
			data.issues_dic[annotated_str][col['IssueID']] = []
	
	issue = msg[0]
	found = False
	for type in data.issues_dic:
		if issue in data.issues_dic[type]:
			output = "Issue "+issue+" found in " + type
			if len(data.issues_dic[type][issue]) > 0:
				output += ": " + str(data.issues_dic[type][issue])
			print(output + ".")
			found = True
	if not found:
		print('Issue not found in IssuesDataset.')
	print()