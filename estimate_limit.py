#!/usr/bin/env python3

import sys
import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
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
    print(f"{'='*70}\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--fraction", type=float, default=0.3)
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    df = pd.read_csv(args.csv_file)
    n = df["n"].values
    R = df["density_ratio"].values

    cut_index = int(len(n) * (1 - args.fraction))
    n_tail = n[cut_index:]
    R_tail = R[cut_index:]
    
    x = 1.0 / np.log(n_tail)
    y = R_tail

    slope, intercept, r_value, p_value, std_err_slope = stats.linregress(x, y)
    
    results_filepath = os.path.join(output_dir, f"{script_name}_asymptotic_regression_results.txt")
    with open(results_filepath, "w", encoding="utf-8") as f:
        f.write(f"Estimated Asymptotic Limit (C): {intercept:.12f}\n")
        f.write(f"Convergence Rate Coefficient (a): {slope:.12f}\n")
        f.write(f"R^2: {r_value**2:.8f}\n")
    generated_files.append(results_filepath)

    plt.figure(figsize=(9, 6))
    plt.scatter(x, y, alpha=0.7, label="Empirical Data (Tail)")
    plt.plot(x, slope * x + intercept, linewidth=2, color="#d62728", label="Regression Fit")
    plt.xlabel(r"Transformed Domain $1 / \log(n)$")
    plt.ylabel(r"Density Ratio $R(n)$")
    plt.legend()

    plot_filepath = os.path.join(output_dir, f"{script_name}_regression_plot.png")
    plt.savefig(plot_filepath, dpi=300, bbox_inches="tight")
    generated_files.append(plot_filepath)

    print("\nLIST OF GENERATED FILES:")
    for filepath in generated_files:
        print(f"  >> {os.path.relpath(filepath)}")

if __name__ == "__main__":
    main()
    
    
