import cmds
import webbrowser

@cmds.CMD("Open the given issue in a browser", "open")
def openIssue(msg):
	webbrowser.open("https://issues.apache.org/jira/browse/" + msg[0])
	return

@cmds.CMD("Open the given issue in Github", "git")
def opengit(msg):
	id = msg[0]
	thisType = id.split('-')[0].lower()
	urlBase = "https://github.com/apache/"
	project = "Hadoop"
	if thisType == "cassandra":
		urlBase += "cassandra"
		project = "Cassandra"
	elif thisType == "tajo":
		urlBase += "tajo"
		project = "Tajo"
	else: #assume hadoop
		urlBase += "hadoop"
	
	urlBase += "/search?q=" + id + "&type=commits"
	print("Opening search page for " + id + " in " + project + "...")
	webbrowser.open(urlBase)
	return
