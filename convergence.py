#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
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

def run_analysis():
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_path = os.path.join(output_dir, f"{script_name}_execution.log")
    
    sys.stdout = ExecutionLogger(log_path)
    
    print(f"RUNNING PROGRAM: {' '.join(sys.argv)}")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Assuming log_statistical_analysis_ram was run before
    input_file = os.path.join(output_dir, "log_statistical_analysis_ram_analysis_summary.csv")
    
    if not os.path.exists(input_file):
        print(f"Error: Required data file '{input_file}' not found.")
        return

    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    R = df["density_ratio"].values
    n = df["n"].values
    e_val = math.e

    abs_error = R - e_val
    rel_error = (R / e_val) - 1

    print(f"Analysis Summary for N = {n[-1]}:")
    print(f"  - Final R(n) Value:  {R[-1]:.10f}")
    print(f"  - Target Constant e: {e_val:.10f}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(n, abs_error, marker="o", markersize=4, linestyle='-', linewidth=1.5, color='#1f77b4', label=r'$R(n) - e$')
    plt.axhline(0, color='black', linestyle="--", linewidth=1, alpha=0.7, label='Convergence Target')
    plt.xlabel(r"Sample Size ($n$)", fontsize=12)
    plt.ylabel(r"Absolute Error $R(n) - e$", fontsize=12)
    plt.title(r"Empirical Convergence of Density Ratio $R(n)$ towards $e$", fontsize=14)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    
    plot_path = os.path.join(output_dir, f"{script_name}_convergence_plot.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    summary_text = ["CONVERGENCE TEST SUMMARY\n", f"Timestamp: {datetime.now()}\n", "========================\n\n"]

    x1 = 1 / np.log(n)
    slope1, intercept1, r_val1, p_val1, _ = stats.linregress(x1, R)
    res1 = (f"Model 1: R(n) = a * (1/log n) + b\n"
            f"  - Estimated Limit (b): {intercept1:.10f}\n"
            f"  - Slope (a):           {slope1:.10f}\n"
            f"  - R-squared:           {r_val1**2:.6f}\n\n")
    print(res1)
    summary_text.append(res1)

    report_path = os.path.join(output_dir, f"{script_name}_regression_results.txt")
    with open(report_path, "w") as f:
        f.writelines(summary_text)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE. GENERATED FILES:")
    print(f"  >> {os.path.relpath(plot_path)}")
    print(f"  >> {os.path.relpath(report_path)}")
    print(f"  >> {os.path.relpath(log_path)}")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_analysis()
    
    
