

from collections import defaultdict

from concurrent.futures import ThreadPoolExecutor
from typing import Dict

def generate_pairs(sorted_customers):
    print(f"Generating pairs...")
    permutations = []
    for i in range(len(sorted_customers)):
       for j in range(i+1, len(sorted_customers)):
           c1, c2 = sorted_customers[i], sorted_customers[j]
           permutations.append((c1, c2))
    return permutations

def generate_mapping_for_chunk(items_chunk, k):
    print(f"Generating mappings for {items_chunk} mappings...")
    mapping = defaultdict(list)
    for customer, history in items_chunk:
        match_history = tuple(history[len(history)-k:])
        if len(match_history) < k: continue
        mapping[match_history].append(customer)
    return mapping

def merge_mappings(list_of_dictionaries):
    print(f"Merging {len(list_of_dictionaries)} mappings...")
    final_dict = defaultdict(list)
    for d in list_of_dictionaries:
        for key, value in d.items():
            if value == []: continue
            final_dict[key].extend(value)
    return final_dict

def get_all_friends(customer_to_history_map: Dict, k: int):
    # Task 1: Creating a mapping of unique k-movies to customers.

    items = list(customer_to_history_map.items())
    chunk_size = len(items) // 3

    dictionaries = []
    with ThreadPoolExecutor(3) as executor:
        for i in range(0, len(items), chunk_size):
            chunk = items[i : min(i+chunk_size, len(items))]
            r = executor.submit(generate_mapping_for_chunk, chunk, k)
            dictionaries.append(r)

    list_of_dictionaries = []
    for d in dictionaries:
        list_of_dictionaries.append(d.result())
    k_movies_to_customers = merge_mappings(list_of_dictionaries)
    
    # Task 2: Creating combinations of customers that are friends. 
    permutations = []
    results = []
    with ThreadPoolExecutor(5) as executor: 
        for list_of_customers in k_movies_to_customers.values():
            for customers in list_of_customers:
                sorted_customers = sorted(customers)
                results.append(executor.submit(generate_pairs, sorted_customers))

    for r in results:
        permutations.extend(r.result())
    return permutations

if __name__ == "__main__":
    customer_to_history_map = {
        "c9":  ["m5", "m1", "m3"],
        "c10":  ["m2", "m3"],
        "c11":  ["m2", "m1", "m3"],
        "c12":  ["m5", "m1", "m3"],
        "c1":  ["m1", "m2", "m3"],
        "c2":  ["m2", "m3"],
        "c3":  ["m2", "m1", "m3"],
        "c4":  ["m5", "m1", "m3"],
        "c5":  ["m1", "m2", "m3"],
        "c6":  ["m2", "m3"],
        "c7":  ["m2", "m1", "m3"],
        "c8":  ["m5", "m1", "m3"]
    }

    results = get_all_friends(customer_to_history_map, 2)
    print(results)
