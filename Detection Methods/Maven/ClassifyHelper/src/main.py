import cmds

while True:
    userInput = input("Input command: ").split()

    cmd = userInput[0].lower()
    if not cmd in cmds.commands:
        print("Command not recognized.")
        continue

    cmds.commands[cmd]["fn"](userInput[1:])
