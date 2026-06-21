# Computer Vision Trading Screener

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

**Extracts statistical structure from trading chart images via color segmentation and volatility modeling**

---

## 📋 Overview

High-performance screener that analyzes trading chart images (Noisy Test outputs) and reconstructs statistical behavior from pixel data. Uses color segmentation to extract signal structure, computes correlation metrics and Z-scores, and ranks strategies based on statistical coherence.

### Key Features
- **Color-based Region Extraction** — Isolates signal structures from chart images
- **Statistical Reconstruction** — Recovers mean/dispersion series from pixel data
- **Signal-Distribution Correlation** — Correlates extracted signals with statistical properties
- **Standardized Deviation (Z-Score) Computation** — Normalized scoring across strategies
- **Multi-factor Scoring & Automated Ranking** — Combines multiple metrics for ranking
- **Parallel Processing** — Batch analysis for multiple charts

---

## 🚀 Quick Start

```bash
git clone https://github.com/elbrujo325/computer-vision-trading-screener.git
cd computer-vision-trading-screener
pip install -r requirements.txt

# Place Noisy Test chart images in ./charts/
python cv_screener.py --input charts/ --output results/
```

---

## 📦 Requirements

```
opencv-python
numpy
pandas
openpyxl
scikit-learn
matplotlib
pillow
```

Install via:
```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
computer-vision-trading-screener/
├── cv_screener.py          # Main screener script
├── requirements.txt        # Dependencies
├── LICENSE                 # MIT License
├── README.md               # This file
├── charts/                 # Input chart images (create this)
└── results/                # Output CSV/XLSX (auto-created)
```

---

## 🛠️ Tech Stack

Python · OpenCV · NumPy · Pandas · Scikit-learn · Matplotlib

---

## 📄 License

MIT License — see [LICENSE](./LICENSE)

---

<div align="center">

**By Henry Paolo Alfaro Sotil — Physicist & Data Scientist**

[GitHub](https://github.com/elbrujo325) · [LinkedIn](https://linkedin.com/in/henry-paolo-alfaro-sotil-3b75a9338)

</div>
