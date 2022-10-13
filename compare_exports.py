#!/usr/bin/python

import datetime
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from compare_blocks_helper import compare_blocks
from extract_data_helper import extract_data

# -- variables --
temp_path = "./temp/"  # path to where the zip-files are extracted
number_of_days = 14  # number of days we compare data starting today


# -- functions --
def unzip_zip_file(zip_file):
    zip_file_1_path = Path(zip_file)
    temp_dir_path = base_temp_path / zip_file_1_path.name
    temp_dir_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file_1_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir_path)
    return temp_dir_path


def parse_xml_files_in_directory(xml_files_dir):
    publication_delivery_elements = []
    for xml_file_path in list(xml_files_dir.glob('**/*.xml')):
        publication_delivery_element = ET.parse(str(xml_file_path)).getroot()
        publication_delivery_elements.append(publication_delivery_element)
    return publication_delivery_elements


def get_blocks_by_date(blocks, date):
    matching_blocks = []
    for block in blocks:
        dates = block.dates
        if date in dates:
            matching_blocks.append(block)
    return matching_blocks


# -- validate input --
if len(sys.argv) < 2:
    print("Usage: python3 compare_exports.py path/to/file1.zip path/to/file2.zip")
    sys.exit(0)

# -- unzip --
base_temp_path = Path(temp_path)
file_1 = sys.argv[1]
file_2 = sys.argv[2]
temp_dir_1_path = unzip_zip_file(file_1)
temp_dir_2_path = unzip_zip_file(file_2)

# -- parse xml --
publication_delivery_elements_1 = parse_xml_files_in_directory(temp_dir_1_path)
publication_delivery_elements_2 = parse_xml_files_in_directory(temp_dir_2_path)

# -- extract data --
try:
    blocks_1 = extract_data(publication_delivery_elements_1)
    blocks_2 = extract_data(publication_delivery_elements_2)
except ValueError as err:
    sys.exit(err.args)

# -- compare data --
starting_date = datetime.datetime.today()
no_errors = True

print(f"Comparing blocks for {number_of_days} days starting on {starting_date.date()}")
for i in range(0, number_of_days):
    date_time = starting_date + datetime.timedelta(days=i)
    date_string = date_time.strftime("%Y-%m-%d")
    blocks_for_date_1 = get_blocks_by_date(blocks_1, date_string)
    blocks_for_date_2 = get_blocks_by_date(blocks_2, date_string)

    errors = compare_blocks(blocks_for_date_1, blocks_for_date_2, file_1, file_2)

    if errors:
        no_errors = False
        print(f'Found {len(errors)} errors for {date_string}:')
        for error in errors:
            print(error)

    if len(blocks_for_date_1) == 0 and len(blocks_for_date_2) == 0:
        print(f'The files contain no blocks for {date_string}')

if no_errors:
    print(f'File {file_1} and {file_2} contain equal blocks')
else:
    sys.exit(1)
