# Probabilistic-Prime-Explorer
A computational framework for generating and analyzing prime numbers using optimized state-space exploration and aggressive tree pruning.

[![DOI: Software](https://zenodo.org/badge/DOI/10.5281/zenodo.[INSERISCI_DOI_SOFTWARE].svg)](https://doi.org/10.5281/zenodo.[INSERISCI_DOI_SOFTWARE])
[![DOI: Dataset](https://zenodo.org/badge/DOI/10.5281/zenodo.19382555.svg)](https://doi.org/10.5281/zenodo.19382555)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A computational framework for generating and analyzing structurally constrained prime numbers using optimized state-space exploration and aggressive tree pruning. 

This repository contains the source code, data extraction scripts, and analytical pipeline supporting our computational number theory manuscript. The generation algorithm explores primes of the form $\prod p_i^{a_i} - 1$ via an odometer-like mechanism enhanced with exponent caching and a deterministic 64-bit Miller-Rabin primality test.

---

## 📂 Data & Code Availability

To ensure full reproducibility of our results, the research outputs are distributed as follows:



* **The Manuscript:** Available as a preprint on arXiv: `[arXiv:XXXX.XXXXX]`
* **The Source Code (This Repository):** Hosted on GitHub and permanently archived on Zenodo at `[DOI_SOFTWARE]`.
* **The Raw Dataset (4.3 GB):** Due to the massive scale of the computational logs generated during the state-space exploration (up to $N=8000$), the raw dataset is hosted externally on Zenodo at [https://doi.org/10.5281/zenodo.19382555](https://doi.org/10.5281/zenodo.19382555). It contains the 26 execution logs and the aggregated statistical summaries (`final_results.csv`).

---

## 🏗️ Repository Structure

* `prime_generator_high_rate.py`: The core algorithm. A highly optimized PyPy3 script for probabilistic prime generation and state-space pruning.
* `extract_results.sh`: A Bash pipeline used to parse the massive raw logs and extract 11 core statistical metrics (including F1-Score, Hit Rate, and Domain Space Coverage).
* `[NOME_FILE_ANALISI].py`: Python modules for advanced statistical and structural analysis (e.g., Cramér's model gaps, Chebyshev bias).
* `CITATION.cff`: Citation metadata for researchers using this framework.

---

## 🚀 Quick Start & Reproduction

### Prerequisites
To run the high-rate generator efficiently, we strongly recommend using **PyPy3** instead of standard CPython for massive performance gains.
* PyPy3 (or Python 3.8+)
* Bash environment (for data extraction)
* standard data-science stack (`pandas`, `numpy`, `matplotlib`) for the analytical pipeline.

### 1. Generating Primes
To start exploring the state-space for a specific initial prime set:
```bash
pypy3 prime_generator_high_rate.py
