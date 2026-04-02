#!/usr/bin/env python3

"""
Log Statistical Analysis Tool (Memory Optimized)
==============================================
Designed for high-performance statistical processing of prime-number generation logs.
"""

import os
import re
import sys
import math
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

class ExecutionLogger(object):
    def __init__(self, log_file_path):
        self.terminal = sys.stdout
        self.log = open(log_file_path, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def extract_integer_list(line):
    clean_line = line.strip("# \n\r[]")
    if not clean_line:
        return []
    try:
        return [int(x) for x in clean_line.split(",")]
    except ValueError:
        return []

def parse_log_file(filepath):
    data = {}
    with open(filepath, "r", encoding="utf-8") as f:
        file_iter = iter(f)
        for line in file_iter:
            if "# input value" in line:
                data["n"] = int(next(file_iter).strip())
            elif "# input prime" in line:
                data["input_prime"] = int(next(file_iter).strip())
            elif "# max value" in line:
                data["max_value"] = int(next(file_iter).strip())
            elif "# prime list found" in line:
                data["prime_list_found"] = extract_integer_list(next(file_iter))
            elif "# prime list check" in line:
                data["prime_list_check"] = extract_integer_list(next(file_iter))
            elif "not prime counter" in line:
                match = re.search(r"not prime counter: (\d+) -- prime counter: (\d+)", line)
                if match:
                    data["not_prime_counter"] = int(match.group(1))
                    data["prime_counter"] = int(match.group(2))
    return data

def compute_metrics(data):
    S = data.get("prime_counter", 0) + data.get("not_prime_counter", 0)
    pi_S = data.get("prime_counter", 0)
    rho_S = pi_S / S if S > 0 else 0.0

    primes_found = data.get("prime_list_found", [])
    primes_check = data.get("prime_list_check", [])

    mean_N = np.mean(primes_found) if len(primes_found) > 0 else 0.0
    rho_PNT = 1.0 / math.log(mean_N) if mean_N > 1 else 0.0

    density_ratio = rho_S / rho_PNT if rho_PNT > 0 else 0.0
    coverage = len(primes_found) / len(primes_check) if len(primes_check) > 0 else 0.0

    if len(primes_found) > 1:
        primes_arr = np.sort(np.array(primes_found, dtype=np.int64))
        gaps = np.diff(primes_arr)
        mean_gap = float(np.mean(gaps))
        var_gap = float(np.var(gaps))
    else:
        mean_gap = 0.0
        var_gap = 0.0

    return {
        "n": data.get("n", None),
        "max_value": data.get("max_value", None),
        "search_space_size": S,
        "primes_found": pi_S,
        "empirical_density": rho_S,
        "pnt_density": rho_PNT,
        "density_ratio": density_ratio,
        "coverage_ratio": coverage,
        "mean_gap": mean_gap,
        "variance_gap": var_gap,
    }

def main():
    output_folder = "results"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_file_path = os.path.join(output_folder, f"{script_name}_execution.log")
    
    sys.stdout = ExecutionLogger(log_file_path)

    print(f"RUNNING PROGRAM: {' '.join(sys.argv)}")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    parser = argparse.ArgumentParser(description="Statistical analysis of logs.")
    parser.add_argument("log_directory", nargs="?", help="Path to directory with .log files")
    args = parser.parse_args()

    if not args.log_directory:
        parser.print_help()
        return

    log_dir = args.log_directory
    if not os.path.isdir(log_dir):
        print(f"Error: Target directory '{log_dir}' not found.")
        return

    results_list = []
    generated_files_registry = []

    for filename in os.listdir(log_dir):
        if filename.endswith(".log"):
            filepath = os.path.join(log_dir, filename)
            print(f"[*] Analyzing: {filename}")
            try:
                raw_data = parse_log_file(filepath)
                stats = compute_metrics(raw_data)
                results_list.append(stats)
            except Exception as e:
                print(f"[!] Critical Error in {filename}: {e}")

    if not results_list:
        print("No valid data found.")
        return

    csv_filename = f"{script_name}_analysis_summary.csv"
    csv_path = os.path.join(output_folder, csv_filename)

    df = pd.DataFrame(results_list)
    df = df.sort_values("n")
    df.to_csv(csv_path, index=False)
    
    generated_files_registry.extend([csv_path, log_file_path])

    print("\n--- STATISTICAL SUMMARY ---")
    print(df.to_string(index=False))
    print("-" * 27 + "\n")

    print("LIST OF GENERATED FILES:")
    for file_path in generated_files_registry:
        print(f"  >> {os.path.relpath(file_path)}")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
    
    
