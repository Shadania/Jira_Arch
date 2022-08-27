# read in everything in the new format
added = {}
removed = {}
changed = {}
total = {}
# issue_id,Existence,Property,Executive
for file in ['in/cassandra.csv', 'in/hadoop.csv', 'in/tajo.csv']:
    is_first = True
    with open(file) as f:
        for line in f:
            if is_first:
                is_first = False
                continue
            lineSplit = line.split(',')
            lineSplit = [x.strip() for x in lineSplit]

            result = []

            for i in [1, 2, 3, 4]:
                result.append(str(int(lineSplit[i].split('.')[0]))) 

            if len(lineSplit[5]) > 0:
                result.append("Existence")
            if len(lineSplit[6]) > 0:
                result.append("Property")
            if len(lineSplit[7]) > 0:
                result.append("Executive")

            if int(lineSplit[1].split('.')[0]) > 0:
                added[lineSplit[0]] = result
            if int(lineSplit[2].split('.')[0]) > 0:
                removed[lineSplit[0]] = result
            if int(lineSplit[3].split('.')[0]) > 0:
                changed[lineSplit[0]] = result
            if int(lineSplit[4].split('.')[0]) > 0:
                total[lineSplit[0]] = result

issues = {
    'added': added,
    'removed': removed,
    'changed': changed,
    'total': total
}

# output format: "Issue ID,Type 1,Type 2,Type 3"
for f in ['added.csv', 'removed.csv', 'changed.csv', 'total.csv']:
    with open('./out/' + f, 'w+') as file:
        file.write('Issue ID,Added,Removed,Changed,Total,Type 1,Type 2,Type 3\n')
        for id in issues[f.split('.')[0]]:
            line = id + ','
            line += ','.join(issues[f.split('.')[0]][id])
            file.write(line + '\n')