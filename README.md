# Computer Vision Trading Screener – Noise Test Ranking Engine

## Overview

This project implements a high-performance computer vision screener for quantitative trading strategy evaluation.

The model analyzes trading chart images (Noise Test outputs) and reconstructs statistical behavior directly from pixel data using color segmentation and volatility modeling.

The system:

- Extracts statistical structure from chart images
- Reconstructs mean and dispersion series
- Computes correlation between signal and distribution
- Calculates standardized deviation (Z-score)
- Measures volatility envelope width
- Applies multi-factor scoring
- Ranks strategies automatically
- Uses parallel processing for scalability

The objective is to filter and rank trading strategies based purely on statistical coherence and structural consistency.

---

# How the Model Works

The process is divided into five major phases.

---

## 1️⃣ Region Extraction

The script isolates the relevant area of the chart by cropping:

```python
roi = img[top:bottom, left:right]
```

This removes UI elements and focuses only on the statistical plot.

The image is then converted to HSV color space:

```python
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
```

HSV allows precise color segmentation for signal reconstruction.

---

## 2️⃣ Signal & Distribution Reconstruction

Two masks are created:

- Blue Mask → Signal Line
- Cloud Mask → Distribution Band

```python
blue_mask = cv2.inRange(hsv_roi, blue_lower, blue_upper)
cloud_mask = cv2.bitwise_and(full_color, cv2.bitwise_not(blue_mask))
```

For each sampled X-coordinate:

- The first blue pixel is detected → Signal value
- The cloud pixels are collected → Mean and standard deviation

Statistical reconstruction:

```python
y_signal = altura - blue_pixels[0]
y_mean   = altura - np.mean(cloud_pixels)
y_std    = np.std(altura - cloud_pixels)
```

This transforms pixel space into statistical series.

---

## 3️⃣ Statistical Metrics

Three key quantitative metrics are computed:

### A) Correlation

Measures structural coherence between signal and mean:

```python
corr = np.corrcoef(y_signal, y_mean)[0, 1]
```

High correlation indicates alignment between signal and expected distribution.

---

### B) Z-Score (Final Position)

Standardized distance between signal and distribution:

```python
z_final = (y_signal[-1] - y_mean[-1]) / y_std[-1]
```

This measures statistical extremeness.

---

### C) Volatility Width

Defined as:

```python
ancho_final = y_std[-1] * 4
```

This approximates a 4σ volatility envelope.

---

## 4️⃣ Multi-Factor Scoring System

Each metric is scored independently:

- Correlation score
- Z-score score
- Volatility width score

Weighted final score:

```python
score_final = (
    score_corr * 0.4 +
    score_zscore * 0.35 +
    score_ancho * 0.25
)
```

This creates a structured ranking model instead of binary filtering.

---

## 5️⃣ Filtering Logic

A strategy is approved only if:

```
CORR_MIN <= corr <= CORR_MAX
ZSCORE_MIN <= z_final <= ZSCORE_MAX
ANCHO_MIN <= ancho_final <= ANCHO_MAX
```

This ensures:

- Statistical coherence
- Controlled deviation
- Acceptable volatility structure

---

## 6️⃣ Parallel Processing Engine

The system uses:

```python
ProcessPoolExecutor
```

Tasks are distributed across multiple CPU cores:

```python
NUM_WORKERS = cpu_count() - 1
```

This allows high-speed evaluation of large strategy datasets.

---

## 7️⃣ Ranking Output

The script automatically generates:

- Full ranking
- Approved strategies sheet
- Statistics per asset
- Top 20 summary

Exported to Excel via:

```python
pandas + openpyxl
```

---

# Key Parameters

These can be modified directly in the script:

```
CORR_MIN = 0.80
CORR_MAX = 1.00

ZSCORE_MIN = 0.5
ZSCORE_MAX = 2.80

ANCHO_MIN = 100
ANCHO_MAX = 300.0
```

---

# What This Project Demonstrates

- Computer vision applied to quantitative trading
- Statistical reconstruction from image data
- Multi-factor scoring architecture
- Volatility modeling
- Z-score normalization
- Parallel computing optimization
- Automated ranking system

---

# Requirements

```
opencv-python
numpy
pandas
scipy
openpyxl
```

---

# Performance Design

The model is optimized for:

- Vectorized NumPy operations
- Minimal memory reallocation
- Parallel execution
- Efficient pixel scanning

This allows scalable evaluation of large Noise Test datasets.

---

# Disclaimer

This project is for research and educational purposes only.  
It does not constitute financial advice.
