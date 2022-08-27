# About

This Python script contains functionality to help you while classifying issues.

The project is built as a lightweight commandline tool, and is used accordingly: run the code and you can enter commands. Use the `help` command to view information about available commands.

# Prerequisites
Python must be installed to run this project.

Packages that must also be installed to run this project (`pip install <pkgname>`): `pandas`, `openpyxl`

# Running the Project
Open a commandline inside the `src` folder and execute the program with `python main.py`. Type `help` for all available commands and related information.

# Example Usage of the Combine Command
The Combine Command is used to combine the outputs of the GitIssueFinder and the MavenDependencyAnalyzer into a format that someone can then use to start classifying issues. Example usages of this command with the given present input:

```
combine cassGit cassMaven cassOutput discard-zero
```
This will use the existing `cassGit.txt` and `cassMaven.csv` files in the `resources` folder to generate a `cassOutput.csv` in the `generated` folder. The CSV will list all found issue keys, along with how many (and which) Maven changes were detected per issue. The discard-zero is an optional argument, which, if used, will avoid writing issue keys with a total Maven change count of zero.