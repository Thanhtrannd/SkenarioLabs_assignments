import os
import re
import csv
from PIL import Image

import pytesseract

# String patterns representing total area
# (patterns vary a lot, so this list should be updated for every new case to generalize)
TOTAL_AREA_STRING_PATTERNS = ['total', 'area', 'approx']
AREA_UNITS = {'sqft': ['sq ft', 'sq.ft.', 'sq. feet'],
              'sqm': ['sqm', 'sq.m.', 'sq. metres']}
ALL_AREA_UNITS = sum(AREA_UNITS.values(), [])

# Output
FIELD_NAMES = ['image', 'sqft', 'sqm']
OUTPUT_FILE = './total_area.csv'

# Path to tesseract executable
PATH_TO_TESSERACT = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = PATH_TO_TESSERACT

# IMAGE DIRECTORY
IMAGE_DIR = r"./rawdata"


def get_total_area_from_images(image_dir):
    image_list = os.listdir(image_dir)
    total_area = list()
    for image in image_list:
        print(image)
        string_data = pytesseract.image_to_string(Image.open(f'{IMAGE_DIR}/{image}'))
        matched_string_lines = match_patterns_by_line(string_data, TOTAL_AREA_STRING_PATTERNS)
        matched_unit_lines = match_patterns_by_line(matched_string_lines, ALL_AREA_UNITS)
        area_data = get_area_data_from_line(matched_unit_lines, AREA_UNITS)
        max_area_data = dict()
        max_area_data['image'] = image
        max_area = get_max_area(area_data)
        max_area_data = {**max_area_data, **max_area}
        total_area.append(max_area_data)
    write_to_csv(total_area, FIELD_NAMES, OUTPUT_FILE)
    print('DONE.')


def write_to_csv(data, field_names, file_name):
    with open(file_name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data)


def match_patterns_by_line(strings, patterns_list, case_insensitive=True):
    matched_lines = set()

    string_lines = set()
    if isinstance(strings, str):
        string_lines = strings.split('\n')
    elif isinstance(strings, (set, list)):
        string_lines = strings

    for line in string_lines:
        line = line.strip()
        for pattern in patterns_list:
            if not re.search(pattern, line, re.IGNORECASE):
                continue
            elif not case_insensitive and not re.search(pattern, line):
                continue
            matched_lines.add(line)
    return matched_lines


def get_area_data_from_line(lines, unit_pattern_list):
    area = dict()
    all_units = sum(unit_pattern_list.values(), [])
    patterns_reg = f"({'|'.join(all_units)}))"
    digit_patterns = '[-+]?(?:\\d*\\.\\d+|\\d+)'
    full_patterns = '[-+]?((?:\\d*\\.\\d+|\\d+)\\s*{unit}'.format(unit=patterns_reg)
    for line in lines:
        try:
            area_data = re.findall(full_patterns, line)
            for matched_digit_unit, matched_unit in area_data:
                for unit in unit_pattern_list:
                    if matched_unit in unit_pattern_list[unit]:
                        digit = re.findall(digit_patterns, matched_digit_unit)
                        digit = digit[0]
                        if unit not in area.keys():
                            area[unit] = list()
                        area[unit].append(digit)
        except:
            pass

    return area


def get_max_area(area_data):
    max_area = dict()
    for unit in area_data:
        max_area[unit] = max(area_data[unit])

    return max_area


if __name__ == '__main__':
    get_total_area_from_images(IMAGE_DIR)
