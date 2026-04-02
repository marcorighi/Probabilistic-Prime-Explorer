#!/usr/bin/env python3

import os
import sys
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

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

def load_summary(csv_path):
    df = pd.read_csv(csv_path)
    df['inv_n'] = 1.0 / df['n']
    df['inv_log_n'] = 1.0 / np.log(df['n'])
    return df

def extract_primes_from_log(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        iterator = iter(f)
        for line in iterator:
            if "# prime list found" in line:
                try:
                    next_line = next(iterator)
                    clean_line = next_line.strip("# \n\r[]")
                    if not clean_line: return []
                    return [int(x) for x in clean_line.split(",")]
                except StopIteration: break
    raise ValueError(f"Prime list not found in {log_path}")

def collect_all_primes(log_dir):
    primes_by_n = {}
    for fname in os.listdir(log_dir):
        if fname.endswith('.log'):
            parts = fname.split('___')
            if len(parts) >= 1 and parts[0].isdigit():
                n = int(parts[0])
                path = os.path.join(log_dir, fname)
                try:
                    primes_by_n[n] = extract_primes_from_log(path)
                except Exception as e:
                    print(f"[!] Error in {fname}: {e}")
    return primes_by_n

def main():
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_path = os.path.join(output_dir, f"{script_name}_execution.log")
    
    sys.stdout = ExecutionLogger(log_path)
    generated_files = [log_path]

    print(f"RUNNING PROGRAM: {' '.join(sys.argv)}")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("summary_csv")
    parser.add_argument("log_directory")
    if len(sys.argv) == 1:
        parser.print_help()
        return
    args = parser.parse_args()

    df = load_summary(args.summary_csv)
    primes_by_n = collect_all_primes(args.log_directory)
    if not primes_by_n: return

    # Density Ratio Plot
    plt.figure(figsize=(10,4))
    slope_log, intercept_log, r_log, p_log, se_log = stats.linregress(df['inv_log_n'], df['density_ratio'])
    plt.plot(df['inv_log_n'], df['density_ratio'], 'o', label='data')
    plt.plot(df['inv_log_n'], intercept_log + slope_log*df['inv_log_n'], 'g-', label='fit')
    plt.xlabel('1/log n'); plt.ylabel('Density ratio'); plt.legend()
    
    plot_density = os.path.join(output_dir, f"{script_name}_density_ratio_fit.png")
    plt.savefig(plot_density, dpi=300, bbox_inches='tight')
    plt.close()
    generated_files.append(plot_density)

    # Gap Analysis
    results = []
    for n, primes in sorted(primes_by_n.items()):
        arr = np.sort(np.array(primes, dtype=np.int64))
        if len(arr) < 2: continue
        gaps = np.diff(arr)
        results.append({'n': n, 'mean_gap': np.mean(gaps)})
    
    df_gaps = pd.DataFrame(results)
    csv_gaps = os.path.join(output_dir, f"{script_name}_gap_analysis.csv")
    df_gaps.to_csv(csv_gaps, index=False)
    generated_files.append(csv_gaps)

    print("\nLIST OF GENERATED FILES:")
    for f in generated_files:
        print(f"  >> {os.path.relpath(f)}")

if __name__ == '__main__':
    main()
    
    
