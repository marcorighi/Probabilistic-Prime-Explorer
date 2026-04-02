# Probabilistic-Prime-Explorer

[![Preprint DOI](https://img.shields.io/badge/Preprint-10.5281/zenodo.19386311-blue)](https://doi.org/10.5281/zenodo.19386311)
[![Software DOI](https://img.shields.io/badge/Software-10.5281/zenodo.19383835-green)](https://doi.org/10.5281/zenodo.19383835)
[![Dataset DOI](https://img.shields.io/badge/Dataset-10.5281/zenodo.19382555-red)](https://doi.org/10.5281/zenodo.19382555)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**High-Rate Prime Generation and Analysis Pipeline** *Submitted to Experimental Mathematics*

This repository contains the source code, analytical pipelines, and theoretical framework for the **Probabilistic-Prime-Explorer**, an optimized multi-radix prime generation algorithm designed to explore heavily structured multiplicative integer subsets.

## 📌 Project Overview

This project presents an empirical and statistical analysis of a specialized prime generation algorithm. Utilizing an optimized multi-radix odometer mechanism coupled with aggressive tree pruning and O(1) power caching, we evaluate candidate integers derived from primorial bounded roots.

By pushing the computational threshold up to n = 8000, we mapped the state-space traversal into an Information Retrieval framework, empirically proving a strict zero-duplication rate and highly enriched precision.

### Key Findings
* **Density Enrichment:** The generated sequence demonstrates a persistent asymptotic enrichment in prime density, converging to a limit of approximately **2.5175 times** the Prime Number Theorem expectation.
* **Fractal Memory:** Topological analysis of the prime gaps reveals an exceptionally high Hurst exponent (**H ≈ 0.73**), strongly rejecting the null hypothesis of a memoryless random walk and indicating significant fractal-like long-range dependence.
* **Algebraic Polarization:** The sequence exhibits an extreme, deterministic Chebyshev bias, demonstrating that the primorial bounds fundamentally break probabilistic residue symmetry.

---

## 📂 Open Science Package

To ensure full reproducibility, this research is distributed across three connected modules:

1. **📄 The Manuscript (Preprint):** Available on Zenodo at [DOI: 10.5281/zenodo.19386311](https://doi.org/10.5281/zenodo.19386311)
2. **💻 The Source Code (This Repo):** Archived version (v1.0.0) at [DOI: 10.5281/zenodo.19383835](https://doi.org/10.5281/zenodo.19383835)
3. **📊 The Dataset:** The massive raw computational logs and extracted statistical summaries (4.3 GB) are hosted on a dedicated Zenodo repository at [DOI: 10.5281/zenodo.19382555](https://doi.org/10.5281/zenodo.19382555)

---

## ⚙️ Installation & Usage

### Prerequisites
Due to the computational intensity of the state-space exploration, the generator is optimized for **PyPy3**. The analytical modules run on standard Python 3.9+.

# Install PyPy3 (Ubuntu/Debian example)
sudo apt-get install pypy3

# Install analytical requirements
pip install numpy pandas scipy matplotlib

Ecco il blocco unico definitivo, aggiornato con l'esempio esatto della struttura delle directory e la nota fondamentale sui nomi dei file di log. 


## 🔬 How to Reproduce the Experiment

The following instructions allow anyone to fully reproduce the data generation and the statistical analysis pipeline exactly as presented in our manuscript.

### Prerequisites
The generation step is extremely CPU-intensive and requires **PyPy3** for optimal execution time. The analysis scripts require a standard Python 3 environment.

# 1. Install PyPy3 (Example for Ubuntu/Debian)
sudo apt-get install pypy3

# 2. Install required Python libraries for analysis
pip install numpy pandas scipy matplotlib


### Step 1: Data Generation (State-Space Exploration)
First, ensure the proper directory structure exists to store the generated outputs:

```bash
mkdir -p results_brpt_server/log_final_result
```

We evaluated the candidate integers across a specific set of threshold values (n). To generate the raw logs for all the tested limits, run the following automated bash loop. The python script will automatically output the timestamped `.log` files into the `results_brpt_server/log_final_result/` directory.

*(Note: Depending on your hardware, running the full sequence up to 8000 may take significant time and RAM).*

```bash
# Run the generator for all manuscript values
for n in 10 20 30 40 50 60 70 80 90 100 200 300 400 500 600 700 800 900 1000 2000 3000 4000 5000 6000 7000 8000; do
    echo "Running generation for n = $n..."
    pypy3 prime_generator_high_rate.py $n lt
done

# Extract and compile the results into a single CSV
bash extract_results.sh
```

**Expected output structure:** After running the generation and extraction steps, your directory structure must look similar to this:

```text
results_brpt_server/
├── final_results.csv
└── log_final_result/
    ├── 10___25_02_26__14_30_42.log
    ├── 20___25_02_26__14_30_42.log
    ├── 30___25_02_26__14_30_42.log
    ├── ...
    └── 8000___27_03_26__21_20_34.log
```
> ⚠️ **Important:** The exact filenames of the `.log` files do not matter, as they are dynamically timestamped by the system upon creation. However, it is crucial that **all** of them are contained within the `log_final_result/` directory, and that the compiled `final_results.csv` is located in the parent `results_brpt_server/` folder.

---

### Step 2: Full Statistical & Topological Analysis Pipeline

Once the raw logs are generated (and `final_results.csv` is compiled), run the following 8 analytical modules in sequential order. Ensure your working directory has a `results/` folder to store all outputs.

**1. Basic Statistical Parsing**
Parses the extracted logs and generates the core statistical summary.
```bash
python log_statistical_analysis_ram.py results_brpt_server/log_final_result/
```
*Generated Files:*
* `results/log_statistical_analysis_ram_analysis_summary.csv`
* `results/log_statistical_analysis_ram_execution.log`

**2. Convergence Analysis**
Calculates the asymptotic behavior and regression metrics.
```bash
python convergence.py
```
*Generated Files:*
* `results/convergence_convergence_plot.png`
* `results/convergence_regression_results.txt`
* `results/convergence_execution.log`

**3. Asymptotic Limit Estimation**
Estimates the prime density enrichment limit using the generated summary.
```bash
python estimate_limit.py results/log_statistical_analysis_ram_analysis_summary.csv
```
*Generated Files:*
* `results/estimate_limit_execution.log`
* `results/estimate_limit_asymptotic_regression_results.txt`
* `results/estimate_limit_regression_plot.png`

**4. Prime Structure Analysis**
Evaluates initial gap topology and basic structural density.
```bash
python prime_structure_analyzer_ram.py results/log_statistical_analysis_ram_analysis_summary.csv results_brpt_server/log_final_result/
```
*Generated Files:*
* `results/prime_structure_analyzer_ram_execution.log`
* `results/prime_structure_analyzer_ram_density_ratio_fit.png`
* `results/prime_structure_analyzer_ram_gap_analysis.csv`

**5. Comprehensive Out-of-Core Analysis**
Core statistical module generating pruning efficiency, autocorrelation, and extreme gap distributions.
```bash
python comprehensive_prime_analysis_ram.py results_brpt_server/log_final_result/
```
*Generated Files:* Includes 23 publication-ready outputs, most notably:
* `results/comprehensive_prime_analysis_ram_analysis_summary.csv`
* `results/comprehensive_prime_analysis_ram_pruning_efficiency.png`
* `results/comprehensive_prime_analysis_ram_asymptotic_fits_comparison.png`
* `results/comprehensive_prime_analysis_ram_found_vs_explored.png`
* `results/comprehensive_prime_analysis_ram_gaps_histogram.png`
* `results/comprehensive_prime_analysis_ram_gap_autocorrelation.png`
* `results/comprehensive_prime_analysis_ram_extreme_gaps.png`
* `results/comprehensive_prime_analysis_ram_log_density.png`
* `results/comprehensive_prime_analysis_ram_spatial_cdf.png`
* `results/comprehensive_prime_analysis_ram_factorization_mean_omega.png`
* `results/comprehensive_prime_analysis_ram_time_scaling.png`

**6. Additional Analysis**
Performs Monte Carlo simulations and Weibull fits for gap distributions.
```bash
python additional_prime_analysis_ram.py results_brpt_server/log_final_result/ results/comprehensive_prime_analysis_ram_analysis_summary.csv
```
*Generated Files:*
* `results/additional_prime_analysis_ram_execution.log`
* `results/additional_prime_analysis_ram_monte_carlo_smooth.csv`
* `results/additional_prime_analysis_ram_monte_carlo_comparison.png`
* `results/additional_prime_analysis_ram_gap_fits.csv`
* `results/additional_prime_analysis_ram_gap_fit_n100.png`
* `results/additional_prime_analysis_ram_explored_analysis.csv`
* `results/additional_prime_analysis_ram_explored_vs_found_cdf.png`

**7. Advanced Mathematical Analysis**
Computes LPF (Largest Prime Factor), modular residues, and 2-Adic valuation.
```bash
python advanced_prime_analysis_ram.py results_brpt_server/log_final_result/ results/comprehensive_prime_analysis_ram_analysis_summary.csv results/additional_prime_analysis_ram_monte_carlo_smooth.csv
```
*Generated Files:*
* `results/advanced_prime_analysis_ram_execution.log`
* `results/advanced_prime_analysis_ram_valuation_analysis.csv`
* `results/advanced_prime_analysis_ram_residue_analysis.csv`
* `results/advanced_prime_analysis_ram_enrichment_factor.csv`
* `results/advanced_prime_analysis_ram_enrichment_factor.png`

**8. Frontier Analysis**
Final module computing the Chebyshev bias, Hurst Exponent, and Cramér's model evaluations across all limits.
```bash
python prime_frontier_analysis_ram.py results_brpt_server/log_final_result/ results/comprehensive_prime_analysis_ram_analysis_summary.csv
```
*Generated Files:* * `results/prime_frontier_analysis_ram_execution.log`
* `results/prime_frontier_analysis_ram_capstone_metrics.csv`
* Generates `_chebyshev_bias_n*.png` and `_cramer_gaps_n*.png` plots for all tested threshold limits (from `n=10` up to `n=8000`).
  
## 📊 Analytical Results Output

The archive `latest_results.tgz` contains the complete output of the 8-stage analytical pipeline. These results form the empirical basis for the figures and tables presented in the manuscript.

### Content Overview
Once extracted, the `results/` directory contains approximately **11MB** of data, including:

* **23+ Core Statistical Plots**: PNG files covering gap distributions, pruning efficiency, and time scaling.
* **Frontier Analysis**: Detailed Chebyshev bias plots (`_chebyshev_bias_n*.png`) and Cramér's model evaluations (`_cramer_gaps_n*.png`) for every threshold from $n=10$ to $n=8000$.
* **Numerical Datasets**: CSV files for each analysis stage (autocorrelations, modular residues, 2-Adic valuations, and enrichment factors).
* **Execution Logs**: Technical logs for every analytical module to ensure full transparency and step-by-step reproducibility.

### How to access the results
To extract the archive and browse the generated plots and data:
```bash
tar -xvzf latest_results.tgz
```
### 📂 Key Files in this Archive (Expanded)

| File Category / Pattern | Description |
| :--- | :--- |
| `log_statistical_analysis_ram_analysis_summary.csv` | **The Core Dataset**: The primary summary containing all fundamental statistics from the raw logs. |
| `prime_frontier_analysis_ram_chebyshev_bias_n*.png` | **Chebyshev Bias**: Visualizations of the oscillation in prime counts for each threshold $n$. |
| `prime_frontier_analysis_ram_cramer_gaps_n*.png` | **Gap Distribution vs Cramér**: Comparison of observed gaps against the classic Cramér probabilistic model. |
| `additional_prime_analysis_ram_monte_carlo_*.png/csv` | **Monte Carlo Simulations**: Results and plots comparing the experimental data with stochastic models. |
| `advanced_prime_analysis_ram_enrichment_factor.*` | **Enrichment Ratio**: Shows how the prime density increases compared to standard distributions. |
| `comprehensive_prime_analysis_ram_gap_autocorrelation.*` | **Autocorrelation**: Analysis of the statistical dependence between successive prime gaps. |
| `comprehensive_prime_analysis_ram_extreme_gaps.*` | **Extreme Value Analysis**: Study of the largest and most rare gaps found in the state-space. |
| `advanced_prime_analysis_ram_valuation_analysis.csv` | **2-Adic Valuation**: Mathematical analysis of the p-adic properties of the generated numbers. |
| `comprehensive_prime_analysis_ram_pruning_efficiency.*` | **Algorithm Performance**: Visual proof of how the Aggressive Tree Pruning reduces the search space. |
| `comprehensive_prime_analysis_ram_spatial_cdf.png` | **Spatial Distribution**: The Cumulative Distribution Function of the primes in the explored space. |
| `*_execution.log` | **Audit Trail**: Technical logs for each script, providing proof of the parameters used and execution time. |



