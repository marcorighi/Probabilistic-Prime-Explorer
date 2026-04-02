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

```bash
# Install PyPy3 (Ubuntu/Debian example)
sudo apt-get install pypy3

# Install analytical requirements
pip install numpy pandas scipy matplotlib
