# Enterprise E-Commerce Business Intelligence & Predictive Analytics Suite

A production-grade, full-stack business intelligence platform integrating real-time data analytics, dynamic machine learning regression models, and an interactive executive dashboard.

## 🚀 Key Features
- **Full-Stack Architecture:** Built with high-performance FastAPI backend and responsive React frontend styled with Tailwind CSS.
- **Machine Learning Integration:** Uses `scikit-learn` Linear Regression trained dynamically on transaction datasets to forecast revenue based on custom volume inputs.
- **Advanced Data Visualization:** Interactive trend lines and distribution graphs powered by `Recharts`.
- **RESTful API Endpoints:** Clean endpoints for real-time analytics aggregation and predictive inference.

## 🛠️ Tech Stack
- **Frontend:** React, Vite, Tailwind CSS, Recharts, Lucide Icons
- **Backend:** Python, FastAPI, Uvicorn, Pandas, Scikit-Learn, NumPy
- **Version Control:** Git / GitHub

## ⚙️ Quick Start Guide

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload