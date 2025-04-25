#!/bin/bash
set -e

python "./workload analyzer/WorkloadParser.py"
python "./knob selector/anonymize.py"
python "./knob selector/knob_select.py"
python "./range pruner/anonymize.py"
python "./range pruner/range_pruner.py"
python "./configuration recommender/LLM_server.py"
python "./configuration recommender/DB_client.py"