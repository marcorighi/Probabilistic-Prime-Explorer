#!/usr/bin/env python3

"""
Comprehensive Prime Analysis (Extreme RAM-Optimized - Full Suite)
=================================================================
Part of the Experimental Mathematics Research Pipeline.
Out-of-Core Processing Edition.

Outputs (saved exclusively to /results):
Generates the complete suite of 23 analytical files (CSV, PNG, TXT).
"""

import os
import sys
import re
import math
import warnings
import gc
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

try:
    from sympy import factorint
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    print("[!] Warning: sympy module not installed. Factorization analysis will be skipped.")

warnings.filterwarnings("ignore", category=RuntimeWarning)

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

# --- MAIN PIPELINE ---

def main():
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    script_prefix = os.path.splitext(os.path.basename(__file__))[0]
    log_file_path = os.path.join(output_dir, f"{script_prefix}_execution.log")

    sys.stdout = ExecutionLogger(log_file_path)
    generated_files = [log_file_path]

    print(f"RUNNING PROGRAM: {' '.join(sys.argv)}")
    print(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}\n")

    if len(sys.argv) != 2:
        print("Usage: python comprehensive_prime_analysis_ram.py <log_directory>")
        sys.exit(1)

    log_dir = sys.argv[1]

    # Dictionaries and lists for global aggregation
    summary_rows, gap_rows, extreme_gaps_rows = [], [], []
    acf_rows, found_explored_rows, fact_rows = [], [], []
    spatial_rows, time_rows, log_density_rows = [], [], []

    plot_data_gaps = []
    plot_data_spatial = {}
    plot_data_acf = {}

    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]

    for fname in sorted(log_files):
        parts = fname.split('___')
        if len(parts) < 1 or not parts[0].isdigit(): continue

        n = int(parts[0])
        path = os.path.join(log_dir, fname)
        print(f"  -> Processing stream for n = {n} ...")

        primes_list, explored_list = [], []
        max_val, not_prime, prime_cnt, exec_time = 0, 0, 0, None
        state = None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if "# prime list found" in line: state = "primes"; continue
                    elif "# prime to explore found" in line: state = "explored"; continue
                    elif line.startswith("# max value"): state = "max_val"; continue
                    elif "Execution time (ms):" in line: state = "exec_time"; continue
                    elif "not prime counter:" in line:
                        match = re.search(r'not prime counter:\s*(\d+)\s*--\s*prime counter:\s*(\d+)', line)
                        if match: not_prime, prime_cnt = int(match.group(1)), int(match.group(2))
                        continue

                    if state in ("primes", "explored"):
                        target_list = primes_list if state == "primes" else explored_list
                        clean_line = line.strip().strip("#").replace('[', '').replace(']', '')
                        ends_here = "]" in line
                        if clean_line:
                            for x in clean_line.split(','):
                                x = x.strip()
                                if x: target_list.append(int(x))
                        if ends_here: state = None

                    elif state == "max_val":
                        match = re.search(r'(\d+)', line)
                        if match: max_val = int(match.group(1))
                        state = None

                    elif state == "exec_time":
                        match = re.search(r'([0-9.]+)', line)
                        if match: exec_time = float(match.group(1))
                        state = None
        except Exception as e:
            continue

        primes = np.array(sorted(primes_list), dtype=np.int64)
        explored = np.array(explored_list, dtype=np.int64)

        S = not_prime + prime_cnt
        rho_S = prime_cnt / S if S > 0 else 0.0
        mean_prime = np.mean(primes) if len(primes) > 0 else 0.0
        rho_PNT = 1.0 / math.log(mean_prime) if mean_prime > 1 else 0.0
        density_ratio = rho_S / rho_PNT if rho_PNT > 0 else 0.0

        gaps = np.diff(primes) if len(primes) > 1 else np.array([])
        mean_gap = np.mean(gaps) if len(gaps) > 0 else 0.0
        var_gap = np.var(gaps) if len(gaps) > 0 else 0.0

        summary_rows.append({
            'n': n, 'max_value': max_val, 'search_space_size': S,
            'primes_found': prime_cnt, 'empirical_density': rho_S,
            'pnt_density': rho_PNT, 'density_ratio': density_ratio,
            'mean_gap': mean_gap, 'variance_gap': var_gap, 'exec_time_ms': exec_time
        })

        if exec_time is not None:
            time_rows.append({'n': n, 'search_space': S, 'exec_time_ms': exec_time})

        if len(primes) > 1:
            std_gap = np.std(gaps)
            cv = std_gap / mean_gap if mean_gap > 0 else 0
            gaps_norm = gaps / mean_gap if mean_gap > 0 else gaps

            if len(gaps_norm) > 10000:
                plot_data_gaps.extend(np.random.choice(gaps_norm, 10000, replace=False))
            else:
                plot_data_gaps.extend(gaps_norm)

            ks_stat, p_value = stats.kstest(gaps_norm, 'expon', args=(0, 1))
            gap_rows.append({
                'n': n, 'num_primes': len(primes), 'mean_gap': mean_gap,
                'std_gap': std_gap, 'cv_gap': cv, 'ks_statistic': ks_stat, 'p_value': p_value
            })

            max_gap = np.max(gaps)
            N_gaps = len(gaps)
            expected_max = np.log(N_gaps) if N_gaps > 0 else 1
            extreme_gaps_rows.append({
                'n': n, 'num_gaps': N_gaps, 'mean_gap': mean_gap, 'max_gap': max_gap,
                'ratio_max_mean': max_gap / mean_gap if mean_gap > 0 else 0,
                'expected_max_logN': expected_max,
                'ratio_to_expected': (max_gap / mean_gap) / expected_max if expected_max > 0 and mean_gap > 0 else 0
            })

            if n <= 200 and len(primes) >= 10:
                acf = np.correlate(gaps_norm - gaps_norm.mean(), gaps_norm - gaps_norm.mean(), mode='full')
                acf = acf[len(acf)//2:]
                if acf[0] != 0: acf = acf / acf[0]
                plot_data_acf[n] = acf[:21]
                acf_rows.append({'n': n, 'acf_lag1': acf[1] if len(acf) > 1 else np.nan})

        if len(explored) > 0:
            found_set = set(primes_list)
            explored_set = set(explored_list)
            inter = len(found_set & explored_set)
            median_exp = np.median(explored)
            frac_above = np.sum(primes > median_exp) / len(primes) if len(primes) > 0 else 0
            found_explored_rows.append({
                'n': n, 'num_explored': len(explored), 'num_found': len(primes),
                'intersection': inter, 'frac_found_above_median': frac_above
            })

        if HAS_SYMPY and n <= 200 and len(primes) >= 10:
            sample = np.random.choice(primes, size=min(500, len(primes)), replace=False)
            omega = []
            for q in sample:
                factors = factorint(int(q)+1)
                omega.append(sum(factors.values()))
            fact_rows.append({
                'n': n, 'sample_size': len(sample), 'mean_omega': np.mean(omega), 'std_omega': np.std(omega)
            })

        if max_val > 0 and len(primes) >= 5:
            scaled = primes / max_val
            ks_s, p_v = stats.kstest(scaled, 'uniform')
            spatial_rows.append({'n': n, 'num_primes': len(primes), 'ks_statistic': ks_s, 'p_value': p_v})
            if n in [100, 500, 1000, 2000]:
                plot_data_spatial[n] = np.sort(np.random.choice(scaled, min(5000, len(scaled)), replace=False))

        if max_val > 1 and len(primes) > 0:
            valid_p = primes[(primes <= max_val) & (primes > 0)]
            sum_inv = np.sum(1.0 / valid_p)
            log_density_rows.append({'n': n, 'log_density': sum_inv / math.log(max_val)})

        del primes_list, explored_list, primes, explored, gaps
        gc.collect()

    print("\n[*] Out-of-Core Parsing complete. Compiling DataFrames and generating full suite of plots...")

    # ==========================================
    # 5. DATA EXPORT AND VISUALIZATION (23 Files)
    # ==========================================

    df_summary = pd.DataFrame(summary_rows).sort_values('n')
    if not df_summary.empty:
        # 1. analysis_summary.csv
        f_sum = out_path('analysis_summary.csv', output_dir, script_prefix)
        df_summary.to_csv(f_sum, index=False); generated_files.append(f_sum)

        # 2 & 3. pruning_efficiency (CSV + PNG)
        df_summary['smooth_density'] = df_summary.apply(lambda r: r['search_space_size']/r['max_value'] if r['max_value']>0 else 0, axis=1)
        f_prun_csv = out_path('pruning_efficiency.csv', output_dir, script_prefix)
        df_summary[['n', 'search_space_size', 'max_value', 'smooth_density']].to_csv(f_prun_csv, index=False); generated_files.append(f_prun_csv)

        plt.figure(figsize=(9, 6))
        plt.plot(df_summary['n'], df_summary['smooth_density'], 'o-', color='#1f77b4', linewidth=2)
        plt.title('Algorithmic Pruning Efficiency'); plt.grid(True, linestyle=':', alpha=0.7)
        f_prun_png = out_path('pruning_efficiency.png', output_dir, script_prefix)
        plt.savefig(f_prun_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_prun_png)

        # 4, 5 & 6. asymptotic_fits (CSV, PNG) & constant_comparison.txt
        valid_df = df_summary[df_summary['n'] > 1].copy()
        if not valid_df.empty:
            valid_df['inv_n'] = 1.0 / valid_df['n']
            valid_df['inv_log_n'] = 1.0 / np.log(valid_df['n'])

            s_n, i_n, r_n, _, _ = stats.linregress(valid_df['inv_n'], valid_df['density_ratio'])
            s_l, i_l, r_l, _, _ = stats.linregress(valid_df['inv_log_n'], valid_df['density_ratio'])

            pd.DataFrame([
                {'model': '1/n', 'limit': i_n, 'slope': s_n, 'r_squared': r_n**2},
                {'model': '1/log(n)', 'limit': i_l, 'slope': s_l, 'r_squared': r_l**2}
            ]).to_csv(out_path('asymptotic_fits.csv', output_dir, script_prefix), index=False)
            generated_files.append(out_path('asymptotic_fits.csv', output_dir, script_prefix))

            plt.figure(figsize=(9, 6))
            plt.plot(valid_df['inv_log_n'], valid_df['density_ratio'], 'o', label='Empirical Data')
            plt.plot(valid_df['inv_log_n'], i_l + s_l * valid_df['inv_log_n'], 'r-', label=f'Fit (limit={i_l:.4f})')
            plt.xlabel('1/log(n)'); plt.ylabel('Density Ratio'); plt.legend(); plt.grid(True, linestyle=':', alpha=0.7)
            f_asy_png = out_path('asymptotic_fits_comparison.png', output_dir, script_prefix)
            plt.savefig(f_asy_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_asy_png)

            f_const = out_path('constant_comparison.txt', output_dir, script_prefix)
            with open(f_const, 'w') as f:
                f.write(f"Empirical Limit (1/log n): {i_l:.6f}\n")
                f.write(f"Euler's e: {math.e:.6f} | Diff: {abs(i_l - math.e):.6f}\n")
                f.write(f"Pi: {math.pi:.6f} | Diff: {abs(i_l - math.pi):.6f}\n")
                f.write(f"2*e^(-gamma): {2*np.exp(-np.euler_gamma):.6f} | Diff: {abs(i_l - 2*np.exp(-np.euler_gamma)):.6f}\n")
            generated_files.append(f_const)

    # 7 & 8. Found vs Explored (CSV + PNG)
    df_fe = pd.DataFrame(found_explored_rows)
    if not df_fe.empty:
        f_fe_csv = out_path('found_vs_explored.csv', output_dir, script_prefix)
        df_fe.to_csv(f_fe_csv, index=False); generated_files.append(f_fe_csv)
        plt.figure(figsize=(9, 6))
        plt.plot(df_fe['n'], df_fe['frac_found_above_median'], 's-', color='#ff7f0e')
        plt.title('Found > Explored Median'); plt.grid(True, linestyle=':', alpha=0.7)
        f_fe_png = out_path('found_vs_explored.png', output_dir, script_prefix)
        plt.savefig(f_fe_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_fe_png)

    # 9 & 10. Gap Analysis & Histogram
    df_gaps = pd.DataFrame(gap_rows)
    if not df_gaps.empty:
        f_gap_csv = out_path('gap_analysis.csv', output_dir, script_prefix)
        df_gaps.to_csv(f_gap_csv, index=False); generated_files.append(f_gap_csv)
    if plot_data_gaps:
        plt.figure(figsize=(9, 6))
        plt.hist(plot_data_gaps, bins=60, density=True, alpha=0.6, color='#2ca02c', edgecolor='black')
        x = np.linspace(0, max(plot_data_gaps), 200)
        plt.plot(x, stats.expon.pdf(x), 'r-', linewidth=2.5)
        plt.title('Normalized Prime Gaps vs Exponential'); plt.grid(True, linestyle=':', alpha=0.7)
        f_hist = out_path('gaps_histogram.png', output_dir, script_prefix)
        plt.savefig(f_hist, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_hist)

    # 11 & 12. Gap Autocorrelation
    df_acf = pd.DataFrame(acf_rows)
    if not df_acf.empty:
        f_acf_csv = out_path('gap_autocorrelation.csv', output_dir, script_prefix)
        df_acf.to_csv(f_acf_csv, index=False); generated_files.append(f_acf_csv)
        plt.figure(figsize=(9, 6))
        for n, acf in plot_data_acf.items(): plt.plot(acf, alpha=0.5, label=f'n={n}')
        plt.title('Gap Autocorrelation (Lag 1-20)'); plt.grid(True, linestyle=':', alpha=0.7)
        f_acf_png = out_path('gap_autocorrelation.png', output_dir, script_prefix)
        plt.savefig(f_acf_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_acf_png)

    # 13 & 14. Extreme Gaps
    df_ext = pd.DataFrame(extreme_gaps_rows)
    if not df_ext.empty:
        f_ext_csv = out_path('extreme_gaps.csv', output_dir, script_prefix)
        df_ext.to_csv(f_ext_csv, index=False); generated_files.append(f_ext_csv)
        plt.figure(figsize=(9, 6))
        plt.plot(df_ext['n'], df_ext['ratio_max_mean'], 'o-', label='Observed Ratio (Max/Mean)')
        plt.plot(df_ext['n'], df_ext['expected_max_logN'], 'k--', label='Expected log(N)')
        plt.title('Extreme Gaps Tail'); plt.legend(); plt.grid(True, linestyle=':', alpha=0.7)
        f_ext_png = out_path('extreme_gaps.png', output_dir, script_prefix)
        plt.savefig(f_ext_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_ext_png)

    # 15 & 16. Log Density
    df_logd = pd.DataFrame(log_density_rows)
    if not df_logd.empty:
        f_logd_csv = out_path('log_density.csv', output_dir, script_prefix)
        df_logd.to_csv(f_logd_csv, index=False); generated_files.append(f_logd_csv)
        plt.figure(figsize=(9, 6))
        plt.plot(df_logd['n'], df_logd['log_density'], 'o-', color='#e377c2')
        plt.title('Logarithmic Density Evolution'); plt.grid(True, linestyle=':', alpha=0.7)
        f_logd_png = out_path('log_density.png', output_dir, script_prefix)
        plt.savefig(f_logd_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_logd_png)

    # 17 & 18. Spatial CDF
    df_sp = pd.DataFrame(spatial_rows)
    if not df_sp.empty:
        f_sp_csv = out_path('spatial_distribution.csv', output_dir, script_prefix)
        df_sp.to_csv(f_sp_csv, index=False); generated_files.append(f_sp_csv)
        plt.figure(figsize=(9, 6))
        for n, data in plot_data_spatial.items():
            plt.step(np.sort(data), np.arange(1, len(data)+1)/len(data), label=f'n={n}', alpha=0.7)
        plt.plot([0, 1], [0, 1], 'k--', label='Uniform')
        plt.title('Spatial Empirical CDF'); plt.legend(); plt.grid(True, linestyle=':', alpha=0.7)
        f_sp_png = out_path('spatial_cdf.png', output_dir, script_prefix)
        plt.savefig(f_sp_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_sp_png)

    # 19 & 20. Factorization
    df_fact = pd.DataFrame(fact_rows)
    if not df_fact.empty:
        f_fact_csv = out_path('factorization_sample.csv', output_dir, script_prefix)
        df_fact.to_csv(f_fact_csv, index=False); generated_files.append(f_fact_csv)
        plt.figure(figsize=(9, 6))
        plt.errorbar(df_fact['n'], df_fact['mean_omega'], yerr=df_fact['std_omega'], fmt='o-', capsize=4)
        plt.title('Mean Prime Factors (Omega) of q+1'); plt.grid(True, linestyle=':', alpha=0.7)
        f_fact_png = out_path('factorization_mean_omega.png', output_dir, script_prefix)
        plt.savefig(f_fact_png, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_fact_png)

    # 21, 22 & 23. Time Scaling (CSV + 2x PNG)
    df_time = pd.DataFrame(time_rows)
    if not df_time.empty:
        f_time_csv = out_path('time_scaling.csv', output_dir, script_prefix)
        df_time.to_csv(f_time_csv, index=False); generated_files.append(f_time_csv)

        plt.figure(figsize=(9, 6))
        plt.plot(df_time['n'], df_time['exec_time_ms'], 'o-', color='#bcbd22')
        plt.title('Time Scaling vs N'); plt.grid(True, linestyle=':', alpha=0.7)
        f_t1 = out_path('time_scaling.png', output_dir, script_prefix)
        plt.savefig(f_t1, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_t1)

        plt.figure(figsize=(9, 6))
        plt.loglog(df_time['search_space'], df_time['exec_time_ms'], 'o', color='#8c564b')
        plt.title('Execution Time vs Search Space Size (Log-Log)'); plt.grid(True, linestyle=':', alpha=0.7)
        f_t2 = out_path('time_vs_searchspace.png', output_dir, script_prefix)
        plt.savefig(f_t2, dpi=300, bbox_inches='tight'); plt.close(); generated_files.append(f_t2)

    # --- PRINT REGISTRY ---
    print("\n" + "="*75)
    print("COMPREHENSIVE OUT-OF-CORE ANALYSIS COMPLETED SUCCESSFULLY.")
    print("LIST OF PUBLICATION-READY FILES GENERATED:")
    for filepath in generated_files:
        print(f"  >> {os.path.relpath(filepath)}")
    print("="*75 + "\n")

if __name__ == '__main__':
    main()


