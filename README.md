# 👁️ Computer Vision Trading Screener

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE) [![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)

**Extracts statistical structure from trading chart images using color segmentation and volatility modeling**

---

## 📝 Overview

A high-performance screener that analyzes trading chart images (Noise Test outputs) and reconstructs statistical behavior from pixel data. The model uses color segmentation to extract signal structure, computes correlation metrics and Z-scores, and ranks strategies based on statistical coherence.

## 🔑 Key Features

- **Color-based region extraction from chart images**
- **Statistical reconstruction of mean and dispersion series**
- **Signal-distribution correlation analysis**
- **Standardized deviation (Z-score) computation**
- **Volatility envelope width measurement**
- **Multi-factor scoring and automated ranking**
- **Parallel processing for batch analysis**


## 🚀 Quick Start

```bash
git clone https://github.com/elbrujo325/computer-vision-trading-screener.git
cd computer-vision-trading-screener

pip install numpy pandas matplotlib opencv-python pillow

python cv_screener.py --input charts/ --output results/
```

Place your Noise Test chart images in the `charts/` directory and run the screener.

## 🛠️ Tech Stack

Python · OpenCV · NumPy · Pandas · Matplotlib

## 📄 License

This project is licensed under the MIT License — see [LICENSE](./LICENSE) for details.

---

<div align="center">

*By [Henry Paolo Alfaro Sotil](https://github.com/elbrujo325) — Physicist & Data Scientist*

</div>
