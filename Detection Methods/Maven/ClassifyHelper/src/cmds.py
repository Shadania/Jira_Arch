import importlib, sys
from os import listdir
from os.path import isfile, join

commands = {}

def CMD(info, fnName):
    def deco(f):
        if not fnName.lower() in commands:
            commands[fnName.lower()] = {
				"info": info, 
				"fn": f
			}

        def wrp(*args, **kwargs):
            return f(*args, **kwargs)
        return wrp
    return deco

dir = "./modules"
files = [f for f in listdir(dir) if isfile(join(dir, f))]
for file in files:
    if file[-2:] == "py":
        mod = importlib.import_module("modules."+file[:-3], '.')

@CMD("Gives overview of all available commands", "help")
def Help(msg):
    print("\nAvailable commands:")
    for cmd in commands:
        print(" " + cmd + ": " + commands[cmd]["info"])
    print("\n")
    return

@CMD("Exit program", "stop")
def Stop(msg):
    print("Exiting script.")
    sys.exit()
    return