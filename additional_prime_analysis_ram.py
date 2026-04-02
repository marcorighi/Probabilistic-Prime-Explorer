#!/usr/bin/env python3

"""
Additional Prime Analysis (Headless/Server Optimized)
=====================================================
Part of the Experimental Mathematics Research Pipeline.

This module performs sophisticated probabilistic and structural evaluations:
1. Monte Carlo Simulation: Validates empirical prime densities against stochastic
   models within smooth number search spaces.
2. Gap Distribution Fitting: Fits empirical prime gaps to Weibull and Lognormal
   distributions, computing skewness, kurtosis, and KS goodness-of-fit.
3. Explored vs. Found Analysis: Employs two-sample Kolmogorov-Smirnov tests
   to compare the spatial distribution of 'explored' vs 'found' prime sets.

Outputs (saved exclusively to /results):
- High-resolution (300 DPI) statistical plots.
- Data-rich CSV files tracking Monte Carlo Z-scores and gap parameters.
- Appended execution logs for research reproducibility.
"""

import os
import sys
import argparse
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd

# --- SERVER HEADLESS FIX ---
import matplotlib
matplotlib.use('Agg')  # Forces headless rendering to prevent Qt/ICE errors
import matplotlib.pyplot as plt
# ---------------------------

from scipy import stats
from scipy.stats import weibull_min, lognorm, ks_2samp

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

# ------------------------------------------------------------
# 1. LOG PARSING FUNCTIONS (Memory Optimized & Single-Pass)
# ------------------------------------------------------------

def parse_log_for_n(log_dir, n):
    """Stream-parses a specific log file to extract numerical parameters and lists."""
    target_file = None
    for fname in os.listdir(log_dir):
        if fname.startswith(f"{n}___") and fname.endswith('.log'):
            target_file = os.path.join(log_dir, fname)
            break

    if not target_file:
        print(f"[!] Warning: no log file found for n={n}")
        return None

    data = {
        'n': n,
        'p_n': None,
        'max_value': None,
        'primes_found': [],
        'explored': []
    }

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            iterator = iter(f)
            for line in iterator:
                if "# input prime" in line:
                    try:
                        data['p_n'] = int(next(iterator).strip())
                    except StopIteration: break

                elif "# max value" in line:
                    try:
                        data['max_value'] = int(next(iterator).strip())
                    except StopIteration: break

                elif "# prime list found" in line:
                    try:
                        clean_line = next(iterator).strip("# \n\r[]")
                        if clean_line:
                            data['primes_found'] = [int(x) for x in clean_line.split(",")]
                    except StopIteration: break

                elif "# prime to explore found" in line:
                    try:
                        clean_line = next(iterator).strip("# \n\r[]")
                        if clean_line:
                            data['explored'] = [int(x) for x in clean_line.split(",")]
                    except StopIteration: break
    except Exception as e:
        print(f"[!] Warning: could not parse {target_file}: {e}")
        return None

    if data['p_n'] is None or data['max_value'] is None:
        print(f"[!] Warning: missing critical data (p_n or max_value) in {target_file}")
        return None

    return data

# ------------------------------------------------------------
# 2. HELPER FUNCTIONS FOR SMOOTHNESS AND PRIME GENERATION
# ------------------------------------------------------------

def sieve_primes(limit):
    """Generates primes up to a limit using the Sieve of Eratosthenes."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i:limit+1:i] = [False] * ((limit - i*i)//i + 1)
    return [p for p, is_p in enumerate(sieve) if is_p]

def is_smooth(x, primes_list):
    """Determines if a number 'x' is smooth over a given prime basis."""
    if x == 1:
        return True
    n = x
    for p in primes_list:
        if p * p > n:
            break
        while n % p == 0:
            n //= p
    return n == 1 or n <= primes_list[-1]

# ------------------------------------------------------------
# 3. MONTE CARLO SIMULATION
# ------------------------------------------------------------

def monte_carlo_smooth(data_by_n, mc_samples=10000):
    """Simulates random search space traversal to establish baseline densities."""
    results = []
    print(f"[*] Running Monte Carlo Simulation ({mc_samples} samples per valid n)...")
    for n, d in data_by_n.items():
        if d is None:
            continue
        p_n = d['p_n']
        max_val = d['max_value']

        primes_up_to_pn = sieve_primes(p_n)

        smooth_count = 0
        prime_count = 0

        print(f"  -> MC sampling for n={n}...", end=" ", flush=True)
        for _ in range(mc_samples):
            # Target space assumes x is even
            x = np.random.randint(1, max_val // 2) * 2
            if is_smooth(x, primes_up_to_pn):
                smooth_count += 1
                # Check primality of adjacent number (q+1 or q-1 equivalent logic)
                from sympy import isprime as sympy_isprime
                if sympy_isprime(x - 1):
                    prime_count += 1
        print("Done.")

        if smooth_count == 0:
            mc_density = np.nan
            mc_std = np.nan
        else:
            mc_density = prime_count / smooth_count
            mc_std = np.sqrt(mc_density * (1 - mc_density) / smooth_count)

        results.append({
            'n': n,
            'p_n': p_n,
            'max_value': max_val,
            'mc_samples': mc_samples,
            'smooth_found': smooth_count,
            'primes_in_smooth': prime_count,
            'mc_density': mc_density,
            'mc_std': mc_std
        })
    return pd.DataFrame(results)

# ------------------------------------------------------------
# 4. GAP FITTING AND MOMENTS
# ------------------------------------------------------------

def fit_gap_distributions(primes_list):
    """Calculates higher moments (skewness, kurtosis) and fits parametric models (Weibull, Lognormal)."""
    if len(primes_list) < 10:
        return None

    primes_arr = np.sort(np.array(primes_list, dtype=np.int64))
    gaps = np.diff(primes_arr)

    if len(gaps) < 5:
        return None

    skew = float(stats.skew(gaps))
    kurt = float(stats.kurtosis(gaps))

    params_weibull = weibull_min.fit(gaps, floc=0)
    shape_w, loc_w, scale_w = params_weibull
    ks_w = stats.kstest(gaps, 'weibull_min', args=params_weibull).statistic

    params_lognorm = lognorm.fit(gaps, floc=0)
    shape_l, loc_l, scale_l = params_lognorm
    ks_l = stats.kstest(gaps, 'lognorm', args=params_lognorm).statistic

    return {
        'weibull_shape': shape_w,
        'weibull_scale': scale_w,
        'weibull_ks': ks_w,
        'lognorm_shape': shape_l,
        'lognorm_scale': scale_l,
        'lognorm_ks': ks_l,
        'skewness': skew,
        'kurtosis': kurt,
        'num_gaps': len(gaps)
    }

def analyze_all_gaps(data_by_n):
    rows = []
    for n, d in data_by_n.items():
        if d is None or len(d['primes_found']) < 10:
            continue
        res = fit_gap_distributions(d['primes_found'])
        if res:
            res['n'] = n
            rows.append(res)
    return pd.DataFrame(rows)

# ------------------------------------------------------------
# 5. EXPLORED PRIMES ANALYSIS (KS-Test)
# ------------------------------------------------------------

def compare_explored_found(data_by_n):
    """
    Performs 2-sample Kolmogorov-Smirnov tests to evaluate structural
    differences between searched primes and mathematically validated primes.
    """
    rows = []
    for n, d in data_by_n.items():
        if d is None or not d['explored']:
            continue

        found = np.array(d['primes_found'], dtype=np.int64)
        explored = np.array(d['explored'], dtype=np.int64)

        if len(explored) < 5 or len(found) < 5:
            continue

        def _get_ks_stat(e, f):
            try:
                k = ks_2samp(e, f)
                return float(k.statistic), float(k.pvalue)
            except:
                return np.nan, np.nan

        ks_s, ks_p = _get_ks_stat(explored, found)

        rows.append({
            'n': n,
            'num_explored': len(explored),
            'num_found': len(found),
            'mean_explored': float(np.mean(explored)),
            'mean_found': float(np.mean(found)),
            'median_explored': float(np.median(explored)),
            'median_found': float(np.median(found)),
            'ks_statistic': ks_s,
            'p_value': ks_p
        })
    return pd.DataFrame(rows)

# ------------------------------------------------------------
# 6. PLOTTING FUNCTIONS
# ------------------------------------------------------------

def plot_monte_carlo(mc_df, actual_df, output_dir, prefix, registry):
    plt.figure(figsize=(9, 6))
    plt.errorbar(mc_df['n'], mc_df['mc_density'], yerr=1.96*mc_df['mc_std'],
                 fmt='o', capsize=4, label='Monte Carlo Simulation (95% CI)', color='#1f77b4')
    plt.plot(actual_df['n'], actual_df['actual_density'], 's-', label='Empirical Reality', color='#d62728', linewidth=2)
    plt.xlabel(r'Parameter $n$', fontsize=12)
    plt.ylabel('Density of Primes among Smooth Evens', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.title('Monte Carlo Simulated vs Empirical Prime Density', fontsize=14)

    p_path = out_path('monte_carlo_comparison.png', output_dir, prefix)
    plt.savefig(p_path, dpi=300, bbox_inches='tight')
    plt.close()
    registry.append(p_path)

def plot_gap_fit_example(data_by_n, n_example, output_dir, prefix, registry):
    if n_example not in data_by_n or data_by_n[n_example] is None:
        return

    primes = np.sort(np.array(data_by_n[n_example]['primes_found'], dtype=np.int64))
    gaps = np.diff(primes)
    fit_res = fit_gap_distributions(primes)

    if fit_res is None:
        return

    plt.figure(figsize=(9, 6))
    plt.hist(gaps, bins=60, density=True, alpha=0.6, label='Empirical Data', color='#2ca02c', edgecolor='black')
    x = np.linspace(0, max(gaps), 200)

    shape_w, scale_w = fit_res['weibull_shape'], fit_res['weibull_scale']
    plt.plot(x, weibull_min.pdf(x, shape_w, loc=0, scale=scale_w),
             'r-', linewidth=2, label=f'Weibull Fit (shape={shape_w:.2f})')

    shape_l, scale_l = fit_res['lognorm_shape'], fit_res['lognorm_scale']
    plt.plot(x, lognorm.pdf(x, shape_l, loc=0, scale=scale_l),
             'k--', linewidth=2, label=f'Lognormal Fit (shape={shape_l:.2f})')

    plt.xlabel('Prime Gap Size', fontsize=12)
    plt.ylabel('Probability Density', fontsize=12)
    plt.legend()
    plt.title(f'Gap Distribution Modelling for n={n_example}', fontsize=14)
    plt.grid(True, linestyle=':', alpha=0.7)

    p_path = out_path(f'gap_fit_n{n_example}.png', output_dir, prefix)
    plt.savefig(p_path, dpi=300, bbox_inches='tight')
    plt.close()
    registry.append(p_path)

def plot_explored_cdf(data_by_n, n_list, output_dir, prefix, registry):
    plt.figure(figsize=(9, 6))
    plotted = False

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    for idx, n in enumerate(n_list):
        if n not in data_by_n or data_by_n[n] is None or not data_by_n[n]['explored']:
            continue

        found = np.sort(np.array(data_by_n[n]['primes_found'], dtype=np.int64))
        explored = np.sort(np.array(data_by_n[n]['explored'], dtype=np.int64))

        y_found = np.arange(1, len(found)+1) / len(found)
        y_exp = np.arange(1, len(explored)+1) / len(explored)

        c = colors[idx % len(colors)]
        plt.step(found, y_found, where='post', label=f'Found (n={n})', color=c, linewidth=2)
        plt.step(explored, y_exp, where='post', linestyle='--', label=f'Explored (n={n})', color=c, alpha=0.7, linewidth=1.5)
        plotted = True

    if plotted:
        plt.xlabel('Prime Value', fontsize=12)
        plt.ylabel('Empirical Cumulative Distribution Function (CDF)', fontsize=12)
        plt.legend()
        plt.title('Spatial CDF Comparison: Explored vs Found Primes', fontsize=14)
        plt.grid(True, linestyle=':', alpha=0.7)

        p_path = out_path('explored_vs_found_cdf.png', output_dir, prefix)
        plt.savefig(p_path, dpi=300, bbox_inches='tight')
        registry.append(p_path)
    plt.close()

# ------------------------------------------------------------
# MAIN EXECUTION PIPELINE
# ------------------------------------------------------------

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

    parser = argparse.ArgumentParser(description="Additional statistical prime analysis.")
    parser.add_argument("log_dir", help="Directory containing the raw generator .log files")
    parser.add_argument("summary_csv", help="Path to the primary comprehensive summary CSV")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    log_dir = args.log_dir
    summary_csv = args.summary_csv

    if not os.path.isdir(log_dir) or not os.path.isfile(summary_csv):
        print(f"[!] Error: Verify '{log_dir}' is a directory and '{summary_csv}' is a valid file.")
        sys.exit(1)

    try:
        summary_df = pd.read_csv(summary_csv)
    except Exception as e:
        print(f"[!] Error reading summary CSV: {e}")
        sys.exit(1)

    actual_density = {}
    search_space_size = {}
    for _, row in summary_df.iterrows():
        n = int(row['n'])
        actual_density[n] = row['empirical_density']
        search_space_size[n] = row['search_space_size']

    print("[*] Parsing logs streamingly to extract datasets...")
    data_by_n = {}
    for n in summary_df['n']:
        data_by_n[n] = parse_log_for_n(log_dir, n)

    # A. Monte Carlo Module
    print("\n--- Module 1: Monte Carlo Simulation ---")
    mc_samples = 10000
    mc_df = monte_carlo_smooth(data_by_n, mc_samples=mc_samples)

    if not mc_df.empty:
        mc_df['actual_density'] = mc_df['n'].map(actual_density)
        mc_df['search_space_size'] = mc_df['n'].map(search_space_size)
        mc_df['actual_primes'] = mc_df['search_space_size'] * mc_df['actual_density']
        mc_df['z_score'] = (mc_df['actual_density'] - mc_df['mc_density']) / mc_df['mc_std']

        csv_path = out_path('monte_carlo_smooth.csv', output_dir, script_prefix)
        mc_df.to_csv(csv_path, index=False)
        generated_files_registry.append(csv_path)
        print(f"[*] Monte Carlo results saved securely.")

        actual_df_plot = summary_df[['n', 'empirical_density']].rename(columns={'empirical_density': 'actual_density'})
        plot_monte_carlo(mc_df, actual_df_plot, output_dir, script_prefix, generated_files_registry)

    # B. Gap Fitting Module
    print("\n--- Module 2: Parametric Gap Distributions ---")
    gap_df = analyze_all_gaps(data_by_n)
    if not gap_df.empty:
        csv_path = out_path('gap_fits.csv', output_dir, script_prefix)
        gap_df.to_csv(csv_path, index=False)
        generated_files_registry.append(csv_path)
        print(f"[*] Parametric gap fitting (Weibull/Lognorm) calculated.")

        # We plot n=100 as a representative example, if it exists
        plot_gap_fit_example(data_by_n, 100, output_dir, script_prefix, generated_files_registry)

    # C. Explored vs Found (KS-Test)
    print("\n--- Module 3: Structural Comparison (Explored vs Found) ---")
    exp_df = compare_explored_found(data_by_n)
    if not exp_df.empty:
        csv_path = out_path('explored_analysis.csv', output_dir, script_prefix)
        exp_df.to_csv(csv_path, index=False)
        generated_files_registry.append(csv_path)
        print(f"[*] Explored vs Found KS-Test results generated.")

        plot_explored_cdf(data_by_n, [100, 500, 1000], output_dir, script_prefix, generated_files_registry)

    # 7. Final Audit Registry Print
    print("\n" + "="*75)
    print("ADDITIONAL ANALYSIS PIPELINE COMPLETED SUCCESSFULLY.")
    print("LIST OF PUBLICATION-READY FILES GENERATED:")
    for filepath in generated_files_registry:
        print(f"  >> {os.path.relpath(filepath)}")
    print("="*75 + "\n")

if __name__ == '__main__':
    main()


