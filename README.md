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

## How the script compares traffic plans
The script does not directly compare the contents of both files because we assume that the two files can contain 
exports for different time periods. Instead the script compares blocks for the nearest 14 operating days, and blocks 
running outside this period are ignored. Here is a detailed description of the comparison algorithm:

The script iterates through a date range of 14 days starting on the day the script runs. For each date the script finds
all blocks running on that date from both files and matches blocks from one file with blocks from the other. Matching is
done by comparing vehicle task id and start time. For each pair of matching blocks the two blocks are compared to each
other with the following checks:
1. Check if the two blocks has the same number of journeys.
2. For each pair of journeys with the same index in the two blocks:
   1. Check if the two journeys have the same number of stops.
   2. For each pair of stop points with the same index in the two journeys:
      1. Check if the two stop points have the same quay ref.
      2. Check if the two stop points have the same departure time.

The exports are considered equal if all pairs of matching blocks satisfy the checks above and if for every block in 
either file there exists a matching block in the other file.

## FAQ
Q: Does the message `The files contain no blocks for <some date>` indicate an error?  
A: No. Because the time window the script uses for comparing blocks is based on the date the script runs it often
extends the export periods of the two files. Therefore it is common that the two files does not contain blocks for the 
last few days in the window.

Q: I got an error that looks like this:
```
Traceback (most recent call last):
  File "C: \compare_exports.py", line 62, in <module>
    blocks_1 = extract_data(publication_delivery_elements_1)
  File "C:\ extract_data_helper.py", line 18, in extract_data
    blocks = extract_blocks(publication_delivery_elements, date_type_map, journey_map)
  File "C:\ extract_data_helper.py", line 54, in extract_blocks
    dates.append(date_type_map[day_type_ref])
KeyError: 'RUT:DayType:2022-09-21'
```
What does it mean and does it indicate that the files contain different data?  
A: If the error begins with `Traceback (most recent call last):` it is a technical error, and not a comparison error.
Usually they arise when the script is parsing blocks from the export files and the reason is usually one of two things:
1. One of the files does not follow the expected format. If the files do not contain all the information the script
requires or if they are structured in a different way than what the script expects the script will fail.
2. One of the exports is inconsistent/incomplete. This can happen if a data element references another data element
that has not been included in the export.

Q: The script revealed a difference in the traffic plans. Which plan is right?  
A: There could be an error in the data from either party. The traffic planners must examine their data to check if it
matches the agreed plan.
