# 🧠 Computer Vision Trading Screener

High-performance quantitative screener for trading strategies using computer vision, statistical modeling, and parallel processing.

---

## 📌 Overview

This project implements an automated visual screening system that evaluates trading chart images and ranks strategies using quantitative metrics.

Instead of manually analyzing charts, the system:

• Extracts structured data directly from images  
• Reconstructs statistical series  
• Computes structural metrics  
• Applies a weighted scoring model  
• Generates automated rankings  

---

## 🖥 Core Concept

The system transforms chart images into quantitative datasets using computer vision.

Image → Pixel Extraction → Statistical Reconstruction → Scoring → Ranking

---

## 🔍 Processing Pipeline

### 1️⃣ Region of Interest Detection

The relevant chart area is dynamically cropped using proportional scaling.

---

### 2️⃣ Color Segmentation (HSV Space)

The system identifies:

- Blue mask → Main signal line
- Cloud mask → Volatility region

Using HSV thresholds for robust color detection.

---

### 3️⃣ Pixel-to-Series Transformation

Each valid image column is converted into:

- Main signal value
- Cloud mean value
- Cloud standard deviation

This generates three numerical vectors:

- Signal vector
- Mean cloud vector
- Volatility vector

---

### 4️⃣ Statistical Metrics Computed

For each strategy:

• Pearson Correlation (structure alignment)  
• Final Z-Score (relative deviation)  
• Cloud Width (volatility proxy)  

---

### 5️⃣ Weighted Scoring Model

Final score is computed as:

Score =  
0.40 × Correlation Score  
+ 0.35 × Z-Score Score  
+ 0.25 × Volatility Score  

This creates a multi-factor quantitative evaluation system.

---

### 6️⃣ Strategy Filtering

Strategies must satisfy:

- Correlation range
- Z-Score bounds
- Volatility width limits

Only qualifying strategies are marked as approved.

---

### 7️⃣ Parallel Processing

The system leverages all available CPU cores using:

- multiprocessing
- ProcessPoolExecutor

This enables scalable analysis of hundreds or thousands of chart images efficiently.

---

## 📊 Output

The screener automatically generates an Excel report containing:

- Complete ranking
- Approved strategies only
- Statistics per asset
- Top 20 best strategies

---

## 📂 Supported Folder Structures

Flat structure:

RESULTADOS/
  Asset Strategy/
    NoisseTrade.png

Hierarchical structure:

RESULTADOS/
  Asset/
    Strategy/
      NoisseTrade.png

The system automatically detects the structure.

---

## 🚀 Installation

```bash
pip install -r requirements.txt
