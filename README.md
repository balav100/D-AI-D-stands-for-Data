
 D-AI: Intelligent Data Analytics Platform

> D-AI (Data AI) is an AI-powered data analytics platform that simplifies data preprocessing, visualization, anomaly detection, and dataset exploration through Large Language Models (LLMs). Built with Streamlit, D-AI enables users to upload datasets, generate insights, interact using natural language, and export professional reports—all from a single web application.

---

## 📖 Overview

Analyzing datasets often requires multiple tools for cleaning, visualization, reporting, and interpretation. D-AI combines these tasks into a single AI-powered platform that helps users understand their data without writing extensive code.

The platform supports intelligent preprocessing, interactive visualizations, AI-powered dataset Q&A, voice interaction, anomaly detection, simulation of data changes, and automated PDF report generation.

---

# ✨ Features

## 📂 Dataset Management
- Upload CSV and Excel datasets
- Secure user authentication using Firebase
- Store uploaded datasets in Firebase Realtime Database
- Dataset preview and summary generation

---

## 🧹 Intelligent Data Preprocessing

- Remove duplicate records
- Handle missing values using:
  - Mean Imputation
  - Median Imputation
  - KNN Imputation
  - Row Deletion
  - Column Deletion

---

## 📊 Interactive Visualizations

Supports multiple visualization techniques:

- Histogram
- Box Plot
- Bar Chart
- Pie Chart
- Scatter Plot
- Line Chart
- Correlation Heatmap
- Pair Plot
- PCA Visualization

---

## 🤖 AI Dataset Assistant

Powered by **Llama 3 via Ollama**

Users can ask questions like:

- What are the important columns?
- Describe this dataset.
- Which features are numeric?
- Give insights about missing values.
- Explain the correlation.

The assistant answers in natural language using dataset statistics.

---

## 🎤 Voice Assistant

Supports speech interaction by integrating:

- Speech Recognition
- Google Text-to-Speech (gTTS)

Users can ask questions using their microphone and receive spoken AI responses.

---

## 🔍 Anomaly Detection

Detects unusual observations using:

- Isolation Forest

Useful for:

- Fraud Detection
- Outlier Identification
- Data Quality Analysis

---

## 🔮 What-If Simulator

Allows users to:

- Modify numerical features
- Simulate different scenarios
- Generate new datasets
- Download simulated CSV files

---

## 📄 Automated PDF Reports

Generate professional reports containing:

- Dataset Summary
- Statistics
- Generated Visualizations
- Timestamp

---

## 🔐 User Authentication

Firebase Authentication provides:

- User Registration
- Secure Login
- Session Management

---

## ☁️ Cloud Storage

Stores:

- Uploaded datasets
- Chat history
- Voice interaction history
- Simulated datasets

using Firebase Realtime Database.

---

# 🛠️ Tech Stack

### Frontend

- Streamlit

### Backend

- Python

### AI

- Ollama
- Llama 3

### Machine Learning

- Scikit-learn

### Visualization

- Matplotlib
- Seaborn

### Database

- Firebase Authentication
- Firebase Realtime Database

### Voice Processing

- SpeechRecognition
- gTTS

### Report Generation

- ReportLab

---

# 📁 Project Structure

```
D-AI/
│
├── app.py
├── requirements.txt
├── .env
├── reports/
├── README.md
└── screenshots/
```

# 📈 Workflow

```
User Uploads Dataset
        │
        ▼
Data Cleaning
        │
        ▼
Dataset Summary
        │
        ▼
Visualization
        │
        ▼
AI Chat Assistant
        │
        ▼
Voice Assistant
        │
        ▼
Anomaly Detection
        │
        ▼
What-if Simulation
        │
        ▼
PDF Report Generation
```

---
