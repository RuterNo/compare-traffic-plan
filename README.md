# Compare Traffic Plan

## Description
Compare traffic plan is a script that is used to compare the contents of two traffic plan exports on NeTEx format. It is
intended help operators with the task of comparing Ruter's data to their own.

If the operator is not able to export traffic plans on the format the script requires they can either fork the project 
and make changes so that the script accepts one export on Ruters format and one export on their on format, or they can 
simply use the script as inspiration for making their own comparison tool.

compare_export.py is the main script. The other scripts contain helper methods and data classes.

## Usage
Run the script using python and specify the path to the two export-files that should be compared:

```shell
python3 compare_exports.py path/to/file1.zip path/to/file2.zip
```

If any errors are found they will be printed in the output from the script. Errors are grouped on the operating date of
the block they occur on. The script exits with exit code 1 if errors are found.

If no errors are found the script will output `File <name-of-file-1> and <name-of-file-2> contain equal blocks` and 
terminate with exit code 0.

## How the script compares the files
The script extracts the blocks along with journeys from each of the two export files into two list. The script iterates 
through the nearest 14 operating dates starting on the day the script runs and finds all pairs of blocks from the two 
list that have the same vehicle task id and start time and the operating date of the iterator. The blocks in each pair 
are compared to each other using the following checks:
1. Check if the two blocks has the same number of journeys.
2. For each pair of journeys with the same index in the two blocks:
   1. Check if the two journeys have the same number of stops.
   2. For each pair of stop points with the same index in the two journeys:
      1. Check if the two stop points have the same quay ref.
      2. Check if the two stop points have the same departure time.

The files are considered not equal if any pair of matching blocks does not satisfy the checks above or if the script is 
unable to find a match for a block in either file among the blocks in the other file.

