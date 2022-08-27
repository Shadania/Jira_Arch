# Running the Script
- Have python3 and pip3 installed
- Open a commandline in this directory and execute `pip install -r requirements.txt` to install the script dependencies.
- Run all the scripts in order.
	+ 0 installs some other dependencies
	+ 1 analyzes the data and prepares it for statistics
	+ 2 generates the per-method graphs
	+ 3 generates the AK versus non-AK graphs
	
# Folders
- analysis-output: The output from script 1. Input for scripts 2 and 3.
- data: Data to analyze, from all sources. Input for script 1.
- figures: The output graphs from scripts 2 and 3.