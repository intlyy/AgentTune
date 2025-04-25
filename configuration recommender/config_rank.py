import json
import unittest
import configparser
import re
import json

config = configparser.ConfigParser()
config.read('./config.ini')

file_path = config['range pruner']['output_file']
with open(file_path, "r") as f:
    DEFAULT_CONFIG = json.load(f)
#print(DEFAULT_CONFIG)


def process_config_item(item):
    processed = {}

    for key in DEFAULT_CONFIG:
        processed[key] = item.get(key, DEFAULT_CONFIG[key])
    return processed

process_config_item

def sort_list(json_strings):
    raw_data = [json.loads(s) for s in json_strings]
    processed_data = [
        {key: item.get(key, DEFAULT_CONFIG[key]) for key in DEFAULT_CONFIG}
        for item in raw_data
    ]

    if not processed_data:
        return []

    NUMERIC_KEYS = [
        key for key, value in DEFAULT_CONFIG.items()
        if isinstance(value['min_value'], (int, float))
    ]

    averages = {}
    for k in NUMERIC_KEYS:
        values = [item[k] for item in processed_data]
        averages[k] = sum(values) / len(values)

    rank_dicts = {}
    for k in NUMERIC_KEYS:
        distances = [abs(item[k] - averages[k]) for item in processed_data]
        sorted_distances = sorted(distances)
        
        rd = {}
        prev_dist = None
        current_rank = 1
        for i, dist in enumerate(sorted_distances):
            if dist != prev_dist:
                current_rank = i + 1
                prev_dist = dist
            rd[dist] = current_rank
        rank_dicts[k] = rd

    sum_ranks = []
    for item in processed_data:
        total = 0
        for k in NUMERIC_KEYS:
            dist = abs(item[k] - averages[k])
            total += rank_dicts[k][dist]
        sum_ranks.append(total)


    sorted_pairs = sorted(zip(sum_ranks, processed_data), key=lambda x: x[0])
    sorted_processed_data = [item for _, item in sorted_pairs]
    
    k = config['configuration recommender']['top_k']
    return sorted_processed_data[:k]
