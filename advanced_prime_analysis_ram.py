#!/usr/bin/env python3

"""
Advanced Prime Analysis (Memory Optimized & Mathematical Profiling)
===================================================================
Part of the Experimental Mathematics Research Pipeline.

This module performs deep structural evaluations of prime generators:
1. 2-Adic Valuation: Analyzes the maximum power of 2 dividing (q+1).
2. Modular Residues: Chi-square tests on prime residues modulo small primes (3, 5, 7, 11).
3. Largest Prime Factor (LPF): Evaluates the smoothness of (q+1) using SymPy.
4. Enrichment Factor: Compares empirical densities to Monte Carlo baselines.

Outputs (saved exclusively to /results):
- Aggregated CSV files tracking valuations, residues, and enrichment.
- High-resolution (300 DPI) plotting of the Enrichment curve.
- Appended execution logs for research reproducibility.
"""

import os
import sys
import re
import argparse
from datetime import datetime

import numpy as np
import pandas as pd

# Headless rendering for server environments
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scipy import stats

# Attempt to import sympy for rigorous factorization
try:
    from sympy import factorint
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    print("[!] Warning: sympy not installed. Largest Prime Factor (LPF) analysis will be restricted.")

# --- SYSTEM LOGGING ---

class ExecutionLogger(object):
    """
    Captures standard output and appends it to a persistent log file.
    Ensures absolute reproducibility and preserves terminal output for audits.
    """
    def __init__(self, log_file_path):
        self.terminal = sys.stdout
        self.log = open(log_file_path, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# --- UTILITIES ---

def out_path(base_name, output_dir, prefix):
    """Formats the output path enforcing the standardized naming convention."""
    return os.path.join(output_dir, f"{prefix}_{base_name}")

# --- MEMORY-OPTIMIZED PARSERS (Lazy Loading) ---

def stream_primes_from_log(filepath):
    """
    Yields primes one by one directly from the file stream.
    Vital for processing massive mathematical datasets that exceed available RAM.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        state = 0
        for line in f:
            if state == 0 and "# prime list found" in line:
                state = 1
                continue
            if state == 1:
                clean_line = line.strip(" \n\r#")
                is_end = "]" in clean_line
                clean_line = clean_line.replace('[', '').replace(']', '')
                
                if clean_line:
                    for x in clean_line.split(','):
                        x = x.strip()
                        if x:
                            yield int(x)
                
                if is_end:
                    break

def extract_pn_from_log(filepath):
    """Extracts the input parameter p_n from the log header efficiently."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read(4096)
        match = re.search(r'# input prime\n(\d+)', content)
        return int(match.group(1)) if match else None

# --- MATHEMATICAL ANALYSES ---

def get_v2(q):
    """Computes the 2-adic valuation of (q+1)."""
    m = q + 1
    v = 0
    if m == 0: 
        return 0
    while m > 0 and m % 2 == 0:
        m //= 2
        v += 1
    return v

def process_n_analysis(n, log_path, small_primes=[3, 5, 7, 11]):
    """
    Processes the prime stream for a specific 'n', computing valuations, 
    residues, and LPF distributions with memory efficiency.
    """
    lpf_list = []
    v2_list = []
    residues = {p: [] for p in small_primes}
    count = 0
    max_q = 0

    for q in stream_primes_from_log(log_path):
        count += 1
        if q > max_q: 
            max_q = q
        
        # 2-adic valuation mapping
        v = get_v2(q)
        if v > 0: 
            v2_list.append(v)
        
        # Moduli Residues
        for p in small_primes:
            if q % p != 0:
                residues[p].append(q % p)
        
        # Largest Prime Factor (LPF) Subsampling (First 10,000 to save CPU/Memory)
        if HAS_SYMPY and count <= 10000:
            factors = factorint(q + 1)
            if factors:
                lpf_list.append(max(factors.keys()))

    # Aggregate Results
    v2_stats = None
    if v2_list:
        total_v = len(v2_list)
        # Create an expected geometric distribution for KS-Test
        geom_sample = [] 
        max_v = max(v2_list)
        for k in range(1, max_v + 1):
            geom_sample.extend([k] * max(1, int(round(total_v / (2**k)))))
            
        if len(geom_sample) > 0 and len(v2_list) > 0:
            ks_v2, p_v2 = stats.ks_2samp(v2_list, geom_sample)
            v2_stats = {'n': n, 'num': total_v, 'mean': np.mean(v2_list), 'ks_statistic': ks_v2, 'p_value': p_v2}

    res_stats = []
    for p, r_list in residues.items():
        if r_list:
            # Expected discrete uniform distribution for non-zero residues
            obs = [r_list.count(r) for r in range(1, p)]
            expected = len(r_list) / (p - 1)
            chi2, p_val = stats.chisquare(obs, [expected]*(p-1))
            res_stats.append({'n': n, 'p_mod': p, 'chi2_statistic': chi2, 'p_value': p_val})

    return v2_stats, res_stats, lpf_list, count, max_q

# --- MAIN EXECUTION PIPELINE ---

def main():
    # 1. Output Routing & Persistent Logging Setup
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    
    script_prefix = os.path.splitext(os.path.basename(__file__))[0]
    log_file_path = os.path.join(output_dir, f"{script_prefix}_execution.log")
    
    sys.stdout = ExecutionLogger(log_file_path)
    generated_files_registry = [log_file_path]

    # LOG HEADER
    print(f"RUNNING PROGRAM: {' '.join(sys.argv)}")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}\n")

    parser = argparse.ArgumentParser(description="Advanced mathematical structural profiling.")
    parser.add_argument("log_dir", help="Directory containing raw log files")
    parser.add_argument("summary_csv", help="Path to the comprehensive analysis summary CSV")
    parser.add_argument("monte_carlo_csv", help="Path to the Monte Carlo smooth CSV")
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
        
    args = parser.parse_args()

    # Path validations
    for path_val in [args.log_dir, args.summary_csv, args.monte_carlo_csv]:
        if not os.path.exists(path_val):
            print(f"[!] Critical Error: Path '{path_val}' does not exist.")
            sys.exit(1)

    print("[*] Initiating Advanced Mathematical Profiling...\n")

    summary_df = pd.read_csv(args.summary_csv)
    n_values = sorted(summary_df['n'].unique())
    
    all_v2 = []
    all_res = []
    
    # Module 1 & 2: Structural Iteration
    print("--- Running 2-Adic Valuation & Modular Residue Tests ---")
    for n in n_values:
        log_file = None
        for fname in os.listdir(args.log_dir):
            if fname.startswith(f"{n}___") and fname.endswith('.log'):
                log_file = os.path.join(args.log_dir, fname)
                break
        
        if log_file:
            print(f"  -> Profiling stream for n={n}...")
            v2_s, res_s, lpf_l, count, max_q = process_n_analysis(n, log_file)
            
            if v2_s: 
                all_v2.append(v2_s)
            if res_s:
                all_res.extend(res_s)

    # Export Structural Results
    if all_v2:
        csv_v2 = out_path('valuation_analysis.csv', output_dir, script_prefix)
        pd.DataFrame(all_v2).to_csv(csv_v2, index=False)
        generated_files_registry.append(csv_v2)
        
    if all_res:
        csv_res = out_path('residue_analysis.csv', output_dir, script_prefix)
        pd.DataFrame(all_res).to_csv(csv_res, index=False)
        generated_files_registry.append(csv_res)

    # Module 3: Enrichment Analysis vs Monte Carlo
    print("\n--- Running Enrichment Analysis ---")
    mc_df = pd.read_csv(args.monte_carlo_csv)
    df_enrich = mc_df[['n', 'actual_density', 'mc_density']].copy()
    
    # Enrichment factor = Empirical Density / Simulated Baseline Density
    df_enrich['enrichment_factor'] = df_enrich['actual_density'] / df_enrich['mc_density']
    
    csv_enrich = out_path('enrichment_factor.csv', output_dir, script_prefix)
    df_enrich.to_csv(csv_enrich, index=False)
    generated_files_registry.append(csv_enrich)

    # High-Resolution Scientific Plotting for Enrichment
    plt.figure(figsize=(9, 6))
    plt.plot(df_enrich['n'], df_enrich['enrichment_factor'], 'o-', linewidth=2, color='#9467bd', label='Empirical vs MC')
    plt.axhline(1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Baseline Expectation (1.0)')
    
    plt.xlabel(r'Parameter $n$', fontsize=12)
    plt.ylabel('Enrichment Factor (Empirical / Simulated)', fontsize=12)
    plt.title('Prime Density Enrichment relative to Monte Carlo Expectation', fontsize=14)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    
    plot_enrich = out_path('enrichment_factor.png', output_dir, script_prefix)
    plt.savefig(plot_enrich, dpi=300, bbox_inches='tight')
    plt.close()
    generated_files_registry.append(plot_enrich)

    # Final Audit Registry Print
    print("\n" + "="*75)
    print("ADVANCED MATHEMATICAL PROFILING COMPLETED SUCCESSFULLY.")
    print("LIST OF PUBLICATION-READY FILES GENERATED:")
    for filepath in generated_files_registry:
        print(f"  >> {os.path.relpath(filepath)}")
    print("="*75 + "\n")

if __name__ == '__main__':
    main()
    
    
