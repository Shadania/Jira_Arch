project_counts = {
    "CASSANDRA": 0,
    "HADOOP": 0,
    "HDFS": 0,
    "YARN": 0,
    "MAPREDUCE": 0,
    "TAJO": 0
}

no_ak_project_counts = {
    "CASSANDRA": 0,
    "HADOOP": 0,
    "HDFS": 0,
    "YARN": 0,
    "MAPREDUCE": 0,
    "TAJO": 0
}
ak_project_counts = {
    "CASSANDRA": 0,
    "HADOOP": 0,
    "HDFS": 0,
    "YARN": 0,
    "MAPREDUCE": 0,
    "TAJO": 0
}

with open('total.csv') as f:
    for line in f:
        lineSplit = [x for x in line.strip().split(',') if x]
        key = lineSplit[0]
        project = key.split('-')[0]
        if project not in project_counts:
            print(project + " not found!!")
            continue
        project_counts[project] += 1
        if len(lineSplit) > 5:
            ak_project_counts[project] += 1
        else:
            no_ak_project_counts[project] += 1

print("Total:")
for project in project_counts:
    print(f"{project}: {project_counts[project]}")

print("\nAK:")
for project in ak_project_counts:
    print(f"{project}: {ak_project_counts[project]}")

print("\nNon-AK:")
for project in no_ak_project_counts:
    print(f"{project}: {no_ak_project_counts[project]}")