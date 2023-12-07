# -*- coding: utf-8 -*- 

# external imports
import os
from dotenv import load_dotenv
import json
import re

# Internal import

# ---------- Init ----------
load_dotenv()

INPUT_FILE = os.getenv("FRAMEWORK_INPUT_FILE")
OUTPUT_FOLDER = os.path.abspath(os.getenv("FRAMEWORK_OUTPUT_FOLDER"))
FRAMEWORK_MAPPING_FILE = os.getenv("FRAMEWORK_MAPPING_FILE")
data = json.load(open(FRAMEWORK_MAPPING_FILE, "r", encoding="utf-8"))
regexp_field = r'^(")([^\"]*)(",(?:"[^\"]*",){3}")([^\"]*)(",(?:"[^\"]*",){2}")([^\"]*)(",")([^\"]*)(".*)' #Koha 22.11, tag = 2, mandatory = 4, ind 1 = 6, ind 2 = 8
regexp_subfield = r'^(")([^\"]*)(",")([^\"]*)(",(?:"[^\"]*",){3}")([^\"]*)(",(?:"[^\"]*",){7}")([^\"]*)(",(?:"[^\"]*",){3}")([^\"]*)(".*)' #Koha 22.11, tag = 2, subfield = 2, mandatory = 6, visibility = 8, default_value = 10

# ---------- Func def ----------
def is_empty_ind(ind:str) -> str:
    """Return an emmpty strinf if the character is an underscore"""
    if ind == "_":
        return ""
    return ind

# ---------- Main ----------
for framework in data:
    keep_fields = data[framework]["keep_fields"]
    collapsed_fields = data[framework]["collapsed_fields"]
    mandatory_fields_mapping = data[framework]["mandatory_fields_mapping"]
    default_values_fields_mapping = data[framework]["default_values_fields_mapping"]
    default_fields_inds_mapping = data[framework]["default_fields_inds_mapping"]

    # Convert the mappings to dict
    mandatory_fields = {}
    for field in mandatory_fields_mapping:
        tag = field[0:3]
        mandatory_fields[tag] = []
        for index, char in enumerate(field[3:]):
            mandatory_fields[tag].append(char)
    default_values_fields = {}
    for field in default_values_fields_mapping:
        tag_subfield = field[0:4]
        default_values_fields[tag_subfield] = field[4:]
    default_fields_inds = {}
    for field in default_fields_inds_mapping:
        tag = field[0:3]
        default_fields_inds[tag] = {}
        default_fields_inds[tag]["1"] = is_empty_ind(field[3:4])
        default_fields_inds[tag]["2"] = is_empty_ind(field[4:5])

    # Start editing the file
    is_first_page = True
    page_separator = ""
    with open(f"{OUTPUT_FOLDER}/{framework}_framework.csv", mode="w", encoding="utf-8") as f_out:
        with open(INPUT_FILE, mode="r", encoding="utf-8") as f:
            for index, line in enumerate(f.readlines()):
                # Line separators
                if '"#-#","#-#","#-#","#-#","#-#","#-#","#-#","#-#","#-#","#-#"' in line:
                    is_first_page = False
                    page_separator = line
                    f_out.write(page_separator)
                    continue
                if len(line.split(",")) < 2:
                    f_out.write(line)
                    continue
                # headers : skip
                if '"tagfield"' in line and '"repeatable","mandatory","important"' in line:
                    f_out.write(line)
                    continue
                # Fields
                if is_first_page:
                    has_matched = re.match(regexp_field, line)
                    if has_matched:
                        tag = has_matched.group(2)
                        mandatory = has_matched.group(4)
                        ind1 = has_matched.group(6)
                        ind2 = has_matched.group(8)
                        # MAndatory
                        if tag in mandatory_fields:
                            if len(mandatory_fields[tag]) == 0:
                                mandatory = "1"
                        # Inds
                        if tag in default_fields_inds:
                            ind1 = default_fields_inds[tag]["1"]
                            ind2 = default_fields_inds[tag]["2"]
                        # Output
                        new_line = has_matched.group(1) + tag + has_matched.group(3) + mandatory + has_matched.group(5) + ind1 + has_matched.group(7) + ind2 + has_matched.group(9)
                        f_out.write(new_line + "\n")
                    else:
                        f_out.write(line)
                    continue
                
                # Subfields
                has_matched = re.match(regexp_subfield, line)
                if has_matched:
                    tag = has_matched.group(2)
                    subfield = has_matched.group(4)
                    mandatory = has_matched.group(6)
                    visibility = has_matched.group(8)
                    default_value = has_matched.group(10)
                    # Mandatory
                    if tag in mandatory_fields:
                        if subfield in mandatory_fields[tag]:
                            mandatory = "1"
                    # Visibility
                    if tag in collapsed_fields:
                        visibility = "-1"
                    elif tag not in keep_fields:
                        visibility = "8"
                    # Default values
                    if tag + subfield in default_values_fields:
                        default_value = default_values_fields[tag + subfield]
                    # Output
                    new_line = has_matched.group(1) + tag + has_matched.group(3) + subfield + has_matched.group(5) + mandatory + has_matched.group(7) + visibility + has_matched.group(9) + default_value + has_matched.group(11)
                    f_out.write(new_line + "\n")
                else:
                    f_out.write(line)
