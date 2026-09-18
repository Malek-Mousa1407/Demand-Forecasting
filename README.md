# 📦 Inventory Demand Forecaster

A full-stack machine learning app that predicts inventory restock levels. It uses a decoupled architecture where the frontend and backend are containerized separately, allowing it to process predictions for thousands of items quickly and efficiently.

## 🏗 Architecture & Tech Stack

* **Frontend:** Streamlit (Python 3.11)
* **Backend API:** FastAPI, Uvicorn, Pydantic
* **Machine Learning Engine:** LightGBM (Regression)
* **Data Processing:** Pandas
* **Infrastructure & Deployment:** Docker, Docker Compose, Render Cloud

## ✨ Core Features

* **Fast Batch Predictions:** Uses LightGBM to process up to 10,000 items in under 100ms.
* **API Tracking:** FastAPI middleware calculates the prediction time and returns it via the `X-Predicton-Time` HTTP header.
* **Interactive Dashboard:** A Streamlit UI where you can edit inventory data, view summaries, and easily spot items that need restocking.
* **CSV Export:** Download batch prediction results directly for your records.

## 🚀 Getting Started (Local Development)

### Prerequisites
* [Docker](https://www.docker.com/) and Docker Compose installed on your machine.

### Installation & Execution

1. Clone the repository:
   ```bash
   git clone https://github.com/Malek-Mousa1407/Demand-Forecasting
   cd Demand-Forecasting
   ```

## 🚀 Running the Application on Docker

### 1. Start the Containers

After cloning the github repository, run the following command from the project root:

```bash
docker-compose up --build
```
### 2. Access the application:
- **Frontend UI:** [`http://localhost:8501`](http://localhost:8501)
- **Backend API:** [`http://localhost:8000/docs`](http://localhost:8501/docs)




### 📂 Project Structure
``` bash
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt        # Backend dependencies
│   ├── Dockerfile              # Docker instructions for the API
│   └── model.pkl               # Saved LightGBM model
├── frontend/
│   ├── app.py                  # Streamlit dashboard
│   ├── requirements.txt        # Frontend dependencies
│   └── Dockerfile              # Docker instructions for the UI
├── docker-compose.yaml         # Docker Compose config
└── .gitignore                  # Ignored files
```

### Sample Payload
```bash
[
  {
    "product_id": "ITEM-01",
    "current_stock_level": 15,
    "unit_price_aed": 6500.00,
    "avg_sales_past_week": 22.5,
    "sales_trend_std": 3.1,
    "is_promotion_active": 0,
    "upcoming_holiday_weekend": 1
  }
]
```

### Sample Response
```bash
{
  "predictions": {
    "SKU-TECH-901": 25.4
  }
}
```
##### Author: Malek Mousa