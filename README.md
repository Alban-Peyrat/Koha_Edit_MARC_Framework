# Edit Koha MARC framework

[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)

Generate new Koha MARC frameworks based on an existing framework.
This script allows :

* To keep fields as defined in the existing framework, hide them or collapse them
* To set fields or subfields as mandatory
* To define default values to subfields or indicators

_Note : "hide" fields and not "ignore" them, as [Koha 22.11 documenation](https://koha-community.org/manual/22.11/en/html/administration.html#edit-a-marc-subfield "Read Koha 22.11 documentation about editing a subfield in a MARC framework") states : "When importing records, subfields that are managed in tab 'ignore' will be deleted. If you still wish to keep the subfields, but hide them, use the 'Visibility' options below."_

_Developped for Koha 22.11_

## Non standard library used

The [`python-dotenv`](https://pypi.org/project/python-dotenv/ "Go to python-dotenv Python Package Index page") library is used in the script (`pip install python-dotenv`).

## Configure the JSON setting file

The JSON setting file ([example](./default_framework_example.csv "See example JSON setting file")) is an object containing objects with 5 arrays.

The keys of the first object are the new framework codes (ex : `ART` for an article framework, `THE` for a thesis one, etc.).

Each framework is an object with 5 array elements :

* `keep_fields` : add each field tag as a string, those fields will be kept as they are defined in the original framework (ex : `"009", "200"`)
* `collapsed_fields` : add each field tag as a string, those fields will be collapsed by default (ex : `"009", "200"`)
* `mandatory_fields_mapping` : fields or subfields can be set as mandatory (not both) :
  * To set a __field__ as mandatory, write the field tag as a string (`"{field tag}"`)
  * To set __subfield(s)__ as mandatory, write the field tag followed by all wanted subfields as a string (`"{field tag}{subfield code 1}{subfield code n}"`)
  * For example, setting `["009", "099t", "200af", "700"]` will :
    * Set the whole `009` field as mandatory
    * Set the subfield `t` of the `099` field as mandatory
    * Set the subfields `a` and `f` of the `200` field as mandatory
    * Set the whole `700` field as mandatory
* `default_values_fields_mapping` : add each field tag followed by the subfield followed by the value as a string (`"{field tag}{subfield code}{value}"`) :
  * For example, setting `"099tART"` will set the value `ART` to the subfield `t` of the `099` field
  * Multiple subfields for the same field can be set, just add seperate entries (ex : `"099tART", "099x0"`)
  * Controlfields use `@` as a subfield
* `default_fields_inds_mapping` : add each field tag followed by the two indicators values as a string (`"{field tag}{indicator 1 value}{indicator 2 value}"`) :
  * For example, setting `"71002"` will set the first indicator as `0` and the second as `2` for the field `710`
  * __Use `_` to specify an empty indicator__ (ex : `2000_` will set the first indicator of the `200` field as `0` and will keep the second one empty)

## Execute the script

* Export Koha default framework in a CSV file
* Configure environment variables :
  * `FRAMEWORK_INPUT_FILE` : full path to the default framework CSV file
  * `FRAMEWORK_OUTPUT_FOLDER` : full path to the folder for the new frameworks
  * `FRAMEWORK_MAPPING_FILE` : full path to the JSON setting file
* Run the script
* The output folder will contain all new frameworks as `{CODE}_framework.csv`

## How the scripts works

* Hide fields : for each subfield in the field, set the `hidden` value to `8` (= none of the visibility options are checked)
* Collapse fields : for each subfield in the field, set the `hidden` value to `-1` (= _OPAC_, _Staff Interface_, _Editor_ and _Collapsed_ are checked, _Flagged_ is not)
* If a field is neither hidden or collapased, its `hidden` value stays the same as in the original framework
* Mandatory fields : set the __field__ `mandatory` value to `1`
* Mandatory subfields : set the __subfield__ `mandatory` value to `1`
* _Note : as the script create a `dict` for mandatory fields, writing `"200", "200a"` will not set both the `200` field and its subfield `a` as mandatory. The script sets a field as mandatory if its subfield `list` is empty_
