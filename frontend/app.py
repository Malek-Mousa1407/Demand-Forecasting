import streamlit as st
import pandas as pd
import requests
import os
# --- Configuration ---
API_URL = os.getenv("API_URL", default="http://localhost:8000")

endpoint = f"{API_URL}/predict/expected-demand-many"

st.set_page_config(
    page_title="Inventory Forecaster", 
    page_icon="📦", 
    layout="wide"
)

# --- Header ---
st.title("Inventory Restock Forecaster")
st.markdown("Review your current inventory levels, adjust the parameters, and generate ML-driven restock predictions in a single batch.")

# --- 1. Interactive Input Table ---
# We initialize some starter data in session_state so the table isn't empty
if "input_data" not in st.session_state:
    st.session_state.input_data = pd.DataFrame([
        {
            "product_id": "SKU-TECH-901",
            "current_stock_level": 15,
            "unit_price_aed": 6500.00,
            "avg_sales_past_week": 22.5,
            "sales_trend_std": 3.1,
            "is_promotion_active": 0,
            "upcoming_holiday_weekend": 1
        },
        {
            "product_id": "SKU-TECH-902",
            "current_stock_level": 8,
            "unit_price_aed": 3200.00,
            "avg_sales_past_week": 14.0,
            "sales_trend_std": 1.5,
            "is_promotion_active": 1,
            "upcoming_holiday_weekend": 1
        },
        {
            "product_id": "SKU-HOME-105",
            "current_stock_level": 50,
            "unit_price_aed": 150.00,
            "avg_sales_past_week": 85.0,
            "sales_trend_std": 12.4,
            "is_promotion_active": 0,
            "upcoming_holiday_weekend": 0
        }
    ])

st.subheader("Current Inventory Data")
st.caption("Edit values directly in the table, or add/delete rows before predicting.")

# st.data_editor allows you to modify the dataframe right in the UI
edited_df = st.data_editor(
    st.session_state.input_data, 
    num_rows="dynamic", 
    use_container_width=True,
    hide_index=True
)

st.divider()

# --- 2. Action Button & API Call ---
if st.button("🚀 Predict Restock Amounts", type="primary"):
    with st.spinner("Calculating optimal restock levels..."):
        try:
            # Convert the edited DataFrame into the exact JSON array your backend expects
            payload = edited_df.to_dict(orient="records")

            # Send the POST request
            response = requests.post(endpoint, json=payload)
            response.raise_for_status() # Catches HTTP errors (4xx, 5xx)
            
            predictions = response.json()
            
            # --- 3. Display Results ---
            if predictions:
                st.success("Batch predictions generated successfully!")
                
                # Flatten the nested JSON response into a clean list of dictionaries for pandas
                results_list = []
                for item in predictions:
                    results_list.append({
                        "Product ID": item["Product Info"]["product_id"],
                        "Current Stock": item["Product Info"]["current_stock_level"],
                        "Forecasted Demand": item["Forecasted Weekly Demand"],
                        "Recommended Re-stock": item["Recommended Re-stock Amount"]
                    })
                    
                results_df = pd.DataFrame(results_list)
                
                st.subheader("📊 Restock Recommendations")
                
                # Optional UI Flair: Lightly highlight rows that require restocking
                def highlight_restock(row):
                    if row["Recommended Re-stock"] > 0:
                        # Light red/orange tint for items that need attention
                        return ['background-color: rgba(255, 75, 75, 0.1)'] * len(row)
                    return [''] * len(row)
                    
                # Display the results table with styling
                st.dataframe(
                    results_df.style.apply(highlight_restock, axis=1), 
                    use_container_width=True,
                    hide_index=True
                )
                
            else:
                st.warning("The API returned an empty response.")
                
        except requests.exceptions.ConnectionError:
            st.error(f"Failed to connect to the backend at `{API_URL}`. Is your Docker container currently running?")
        except Exception as e:
            st.error(f"An error occurred: {e}")