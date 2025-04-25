#!/bin/bash
set -e

python "./knob selector/get_candidate_knobs/xml_parser.py"
python "./knob selector/get_candidate_knobs/get_candidate_knobs.py"
python "./knob selector/get_candidate_knobs/simplify_candidate_knobs.py"