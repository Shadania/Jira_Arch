# Running the Script
- Have python3 and pip3 installed
- Open a commandline in this directory and execute `pip install -r requirements.txt` to install the script dependencies.
- Run all the scripts in order, or just run `script_all.py`, which does the same.
	+ 0 installs some other dependencies and updates issues if necessary
	+ 1 analyzes the data and prepares it for statistics
	+ 2 generates the precision graphs
	+ 3 generates the per-method graphs
	+ 4 generates the AK versus non-AK graphs
	
# Folders
- analysis-output: The output from script 1. Input for scripts 2 and 3.
- data: Data to analyze, from all sources. Input for script 1.
- figures: The output graphs from scripts 2 and 3.

# Parameters
`script_shared.py` holds some parameters for the graphics that will be generated.

- `annotated`: Amount of results we will process from each keyword search
- `bottomup`: Amount of results we will process from the source code analysis
- `colors`: Colors used in bar and line charts.
- `hatches`: Patterns used in greyscale bar charts.
- `plot_styles`: Patterns used in greyscale line charts.
- `box_scale`: Should box plots be in linear or logarithmic scale on the Y axis?
- `box_show_outliers`: Show outliers on box plots or not
- `graph_colors`: Use color or greyscale in bar and line plots.
- `font`: Which font should be used in the generated figures?
- `linewidth`: Width of lines in line plots.
- `box_ymax`: Top Y axis limits. Set to None for no limit.