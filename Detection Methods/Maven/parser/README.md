# parser

The parser analyzes a set of annotations that is given in the input file. The output contains results about the architectural knowledge concept, such as "word usage", "co-occurrence" and "keywords". The parser should be given the following arguments:
```
python3 parser.py -i INPUT_FILE
```

## Further explanation of the commands with examples

INPUT_FILE:
- The input file is created by exporting Atlas.ti annotations to a CSV file. The required columns can be found in the provided input files (from the ```input_files``` folder)

## Example sets of arguments
The program can be run using the provided input files (from the ```input_files``` folder) using the following set of arguments:
```
python3 parser.py -i "input_structural.csv"
```
```
python3 parser.py -i "input_technology.csv"
```