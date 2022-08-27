# file name is shorthand for "combine output of the gitlogger + maven analyzer"
import cmds
import res
import csv

@cmds.CMD("Analyze the given filenames. Args: <gitlogger output file name> <maven analyzer file name> <output file name> [discard-zero?]", "combine")
def combineTools(msg):
	git_file = open(res.getFileName('resources\\' + msg[0] + '.txt'), 'r')
	maven = open(res.getFileName('resources\\' + msg[1] + '.csv'), 'r')

	discard_zero = False
	if len(msg) > 3:
		if msg[3] == 'discard-zero':
			discard_zero = True

	# make a dic of the git file
	prev_hash = None
	issue_dic = {} # hash -> [issue_id] 
	for line in git_file:
		if line[0].isspace():
			# not a hash
			stripped = prev_hash.strip()
			if not stripped in issue_dic:
				issue_dic[stripped] = []
			if line.strip() not in issue_dic[stripped]:
				issue_dic[stripped].append(line.strip())
		else:
			prev_hash = line
	git_file.close()


	# go through the maven file line by line
	maven_dic = {}
	for line in maven:
		elements = [x.strip() for x in line.split(',')]
		elements = [x for x in elements if x]

		hash = elements[0]
		if not hash in issue_dic:
			continue # we don't know if this hash has an issue ID, so not interested
		
		# added, removed, updated
		added = int(float(elements[1]))
		removed = int(float(elements[2]))
		updated = int(float(elements[3]))

		issue_ids = issue_dic[hash]
		for id in issue_ids:
			if not id in maven_dic:
				maven_dic[id] = {
					'added': 0,
					'removed': 0,
					'updated': 0,
					'total': 0
				}
			
			maven_dic[id]['added'] += added
			maven_dic[id]['removed'] += removed
			maven_dic[id]['updated'] += updated
			maven_dic[id]['total'] += (added + removed + updated)
	maven.close()

	# discard no-change issues? zeroes?
	if discard_zero:
		keys = list(maven_dic.keys())
		for entry in keys:
			if maven_dic[entry]['total'] == 0:
				del maven_dic[entry]

	# write output
	output = open(res.getFileName('generated\\' + msg[2] + '.csv'), 'w', newline='')
	writer = csv.writer(output)
	writer.writerow(['Issue ID', 'Added', 'Removed', 'Updated', 'Total'])
	for entry in maven_dic:
		writer.writerow([
			entry,
			maven_dic[entry]['added'],
			maven_dic[entry]['removed'],
			maven_dic[entry]['updated'],
			maven_dic[entry]['total']
		])
	output.close()
	print("Done.")
	return True