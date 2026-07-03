import pandas as pd
import numpy as np

print("Generating synthetic supply chain data...")

# Set seed for reproducibility
np.random.seed(42)
n_samples = 5000

# Generate features matching our API schema
data = {
    "current_stock_level": np.random.randint(10, 500, n_samples),
    "unit_price_aed": np.random.uniform(50.0, 3000.0, n_samples),
    "avg_sales_past_week": np.random.uniform(5.0, 100.0, n_samples),
    "sales_trend_std": np.random.uniform(1.0, 20.0, n_samples),
    "is_promotion_active": np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
    "upcoming_holiday_weekend": np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
}

df = pd.DataFrame(data)

# Formulate the Target Variable (What we want to predict)
# Logic: Demand goes up if there's a promo/holiday, and correlates with past sales.
base_demand = df["avg_sales_past_week"] * np.random.uniform(0.8, 1.2, n_samples)
promo_boost = df["is_promotion_active"] * df["avg_sales_past_week"] * 0.5
holiday_boost = df["upcoming_holiday_weekend"] * df["avg_sales_past_week"] * 0.8

# Calculate final target and round to whole units
df["target_demand_next_7d"] = np.round(base_demand + promo_boost + holiday_boost).astype(int)

# Save to CSV
df.to_csv("historical_inventory_data.csv", index=False)
print("✅ Saved 5,000 records to historical_inventory_data.csv")