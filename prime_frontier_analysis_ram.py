#!/usr/bin/env python3

"""
Frontier Prime Analysis (Capstone Module)
=========================================
Part of the Experimental Mathematics Research Pipeline.

This final module applies cutting-edge number theory metrics to the generated sets:
1. Chebyshev's Bias: Cumulative racing of prime residues modulo 3.
2. Cramér's Conjecture: Scaling of record-breaking prime gaps against log^2(p).
3. Hurst Exponent (R/S Analysis): Long-term memory and fractal persistence in gaps.
4. Prime Constellations: Frequency of Twin, Cousin, and Sexy primes.

Outputs (saved exclusively to /results):
- High-resolution (300 DPI) plots for Chebyshev's Bias and Cramér's limit.
- Aggregated CSV tracking Hurst exponents and K-Tuple counts.
- Appended execution logs for research reproducibility.
"""

import os
import sys
import argparse
from datetime import datetime

import numpy as np
import pandas as pd

# Headless rendering for server environments
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- SYSTEM LOGGING ---

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

def out_path(base_name, output_dir, prefix):
    return os.path.join(output_dir, f"{prefix}_{base_name}")

# --- MEMORY-OPTIMIZED PARSER ---

def stream_primes_from_log(filepath):
    """Yields primes robustly and lazily to maintain zero-RAM footprint."""
    with open(filepath, 'r', encoding='utf-8') as f:
        state = 0
        for line in f:
            if state == 0 and "# prime list found" in line:
                state = 1
                continue
            if state == 1:
                clean_line = line.strip(" \n\r#").replace('[', '').replace(']', '')
                is_end = "]" in line
                
                if clean_line:
                    for x in clean_line.split(','):
                        x = x.strip()
                        if x:
                            yield int(x)
                
                if is_end:
                    break

# --- MATHEMATICAL MODULES ---

def estimate_hurst(gaps):
    """
    Estimates the Hurst Exponent using Rescaled Range (R/S) Analysis.
    Assesses long-range dependence in the sequence of prime gaps.
    """
    if len(gaps) < 100:
        return np.nan
        
    gaps_arr = np.array(gaps, dtype=np.float64)
    N = len(gaps_arr)
    max_k = int(np.floor(N / 2))
    
    # We evaluate window sizes logarithmically spaced
    window_sizes = np.logspace(1, np.log10(max_k), 10).astype(int)
    window_sizes = np.unique(window_sizes[window_sizes >= 10])
    
    RS = []
    valid_sizes = []
    
    for w in window_sizes:
        rs_vals = []
        for start in range(0, N - w + 1, w):
            segment = gaps_arr[start:start+w]
            mean_val = np.mean(segment)
            y = segment - mean_val
            Z = np.cumsum(y)
            R = np.max(Z) - np.min(Z)
            S = np.std(segment)
            if S > 0:
                rs_vals.append(R / S)
        if rs_vals:
            RS.append(np.mean(rs_vals))
            valid_sizes.append(w)
            
    if len(valid_sizes) > 3:
        # H is the slope of log(R/S) vs log(window_size)
        coeffs = np.polyfit(np.log(valid_sizes), np.log(RS), 1)
        return float(coeffs[0])
    return np.nan

def process_frontier_metrics(n, log_path, output_dir, prefix, registry):
    """Processes a single log file for all frontier metrics."""
    
    primes = []
    for p in stream_primes_from_log(log_path):
        primes.append(p)
    
    if len(primes) < 10:
        return None
        
    primes = np.array(primes, dtype=np.int64)
    gaps = np.diff(primes)
    
    # 1. Chebyshev's Bias (mod 3)
    mod3_1 = (primes % 3 == 1).cumsum()
    mod3_2 = (primes % 3 == 2).cumsum()
    delta = mod3_2 - mod3_1 # Usually positive in standard primes
    
    if len(primes) > 1000: # Plot only for sufficiently large sets
        plt.figure(figsize=(9, 6))
        plt.plot(range(len(delta)), delta, color='#d62728', linewidth=1.5)
        plt.axhline(0, color='black', linestyle='--')
        plt.xlabel('Prime Index $k$')
        plt.ylabel(r'$\Delta(x) = \pi_{3,2}(x) - \pi_{3,1}(x)$')
        plt.title(f"Chebyshev's Bias (mod 3) Racing for n={n}")
        plt.grid(True, linestyle=':', alpha=0.7)
        plot_path = out_path(f'chebyshev_bias_n{n}.png', output_dir, prefix)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        registry.append(plot_path)

    # 2. Cramér's Conjecture & Record Gaps
    record_indices = []
    record_gaps = []
    current_max = -1
    
    for idx, g in enumerate(gaps):
        if g > current_max:
            current_max = g
            record_gaps.append(g)
            record_indices.append(idx)
            
    if record_gaps and len(record_gaps) > 3:
        record_primes = primes[record_indices]
        cramer_limit = np.log(record_primes)**2
        
        plt.figure(figsize=(9, 6))
        plt.scatter(record_primes, record_gaps, color='#1f77b4', label='Record Gaps', zorder=5)
        plt.plot(record_primes, cramer_limit, 'k--', label=r'Cramér Limit $\sim \log^2(p)$', zorder=4)
        plt.xlabel('Prime $p$')
        plt.ylabel('Record Gap Size')
        plt.title(f"Record Gaps vs Cramér's Conjecture for n={n}")
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)
        cramer_path = out_path(f'cramer_gaps_n{n}.png', output_dir, prefix)
        plt.savefig(cramer_path, dpi=300, bbox_inches='tight')
        plt.close()
        registry.append(cramer_path)

    # 3. Hurst Exponent
    hurst_val = estimate_hurst(gaps)

    # 4. K-Tuples (Constellations)
    gap_counts = pd.Series(gaps).value_counts().to_dict()
    twins = gap_counts.get(2, 0)
    cousins = gap_counts.get(4, 0)
    sexy = gap_counts.get(6, 0)

    return {
        'n': n,
        'total_primes': len(primes),
        'hurst_exponent': hurst_val,
        'chebyshev_final_delta': int(delta[-1]),
        'num_record_gaps': len(record_gaps),
        'max_record_gap': int(record_gaps[-1]) if record_gaps else 0,
        'twin_primes': twins,
        'cousin_primes': cousins,
        'sexy_primes': sexy
    }

# --- MAIN EXECUTION PIPELINE ---

def main():
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    
    script_prefix = os.path.splitext(os.path.basename(__file__))[0]
    log_file_path = os.path.join(output_dir, f"{script_prefix}_execution.log")
    
    sys.stdout = ExecutionLogger(log_file_path)
    generated_files_registry = [log_file_path]

    print(f"RUNNING CAPSTONE PROGRAM: {' '.join(sys.argv)}")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}\n")

    parser = argparse.ArgumentParser(description="Frontier metrics: Chebyshev, Cramér, Hurst, and Constellations.")
    parser.add_argument("log_dir", help="Directory containing raw log files")
    parser.add_argument("summary_csv", help="Path to the comprehensive analysis summary CSV")
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
        
    args = parser.parse_args()

    if not os.path.exists(args.log_dir) or not os.path.exists(args.summary_csv):
        print("[!] Critical Error: Provided paths do not exist.")
        sys.exit(1)

    print("[*] Initiating Frontier Mathematical Profiling...\n")
    summary_df = pd.read_csv(args.summary_csv)
    n_values = sorted(summary_df['n'].unique())
    
    frontier_results = []

    for n in n_values:
        log_file = None
        for fname in os.listdir(args.log_dir):
            if fname.startswith(f"{n}___") and fname.endswith('.log'):
                log_file = os.path.join(args.log_dir, fname)
                break
        
        if log_file:
            print(f"  -> Profiling frontier metrics for n={n}...")
            res = process_frontier_metrics(n, log_file, output_dir, script_prefix, generated_files_registry)
            if res:
                frontier_results.append(res)

    if frontier_results:
        df_frontier = pd.DataFrame(frontier_results)
        csv_path = out_path('capstone_metrics.csv', output_dir, script_prefix)
        df_frontier.to_csv(csv_path, index=False)
        generated_files_registry.append(csv_path)
        print(f"\n[*] Frontier metrics successfully aggregated into {csv_path}")

    print("\n" + "="*75)
    print("FRONTIER MATHEMATICAL PROFILING COMPLETED SUCCESSFULLY.")
    print("LIST OF PUBLICATION-READY FILES GENERATED:")
    for filepath in generated_files_registry:
        print(f"  >> {os.path.relpath(filepath)}")
    print("="*75 + "\n")

if __name__ == '__main__':
    main()
    
    
