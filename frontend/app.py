import streamlit as st
import pandas as pd
import requests
import os

# --- Configuration ---
API_URL = os.getenv("API_URL", default="http://localhost:8000")

# Pointing to your optimized batch prediction endpoint
endpoint = f"{API_URL}/predict/expected-demand"

st.set_page_config(
    page_title="Inventory Forecaster", 
    page_icon="📦", 
    layout="wide"
)

# --- Header ---
st.title("Inventory Restock Forecaster")
st.markdown("Review your current inventory levels, adjust the parameters, and generate ML-driven restock predictions in a single batch.")

# --- 1. Interactive Input Table ---
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
            payload = edited_df.to_dict(orient="records")

            # Generous 120-second timeout to survive cloud cold starts
            response = requests.post(endpoint, json=payload, timeout=120)
            response.raise_for_status()
            
            # 1. Extract the custom middleware timing header
            process_time_raw = response.headers.get("X-Predicton-Time", "N/A")
            try:
                process_time_display = f"{float(process_time_raw):.4f}s"
            except (ValueError, TypeError):
                process_time_display = f"{process_time_raw}s" if process_time_raw != "N/A" else "N/A"
            
            # 2. Extract the dictionary (safely handles both {"predictions": dict} and raw dict returns)
            res_json = response.json()
            predictions_dict = res_json.get("predictions", res_json if isinstance(res_json, dict) else {})
            
            # --- 3. Display Results ---
            if predictions_dict:
                st.success("Batch predictions generated successfully!")
                
                # Map the dictionary predictions directly back to the edited table
                results_df = edited_df[["product_id", "current_stock_level"]].copy()
                results_df = results_df.rename(columns={
                    "product_id": "Product ID", 
                    "current_stock_level": "Current Stock"
                })
                
                # Map forecasted demand from the backend dictionary
                results_df["Forecasted Demand"] = results_df["Product ID"].map(predictions_dict).round(2)
                
                # Calculate recommended restock on the fly (Demand - Current Stock, min 0)
                results_df["Recommended Re-stock"] = (
                    results_df["Forecasted Demand"] - results_df["Current Stock"]
                ).apply(lambda x: max(0, round(x, 2)))
                
                # 3. Four-Column KPI Summary Cards including Inference Time
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Items Scored", f"{len(results_df):,}")
                col2.metric("Total Expected Demand", f"{results_df['Forecasted Demand'].sum():,.0f}")
                col3.metric("Total Units to Restock", f"{results_df['Recommended Re-stock'].sum():,.0f}")
                col4.metric("⚡ Inference Time", process_time_display)
                
                st.subheader("📊 Restock Recommendations")
                
                # Visual highlight logic for items needing restocking
                def highlight_restock(row):
                    if row["Recommended Re-stock"] > 0:
                        return ['background-color: rgba(255, 75, 75, 0.1)'] * len(row)
                    return [''] * len(row)
                    
                st.dataframe(
                    results_df.style.apply(highlight_restock, axis=1), 
                    use_container_width=True,
                    hide_index=True
                )
                
                # CSV export button for batch results
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=results_df.to_csv(index=False).encode('utf-8'),
                    file_name="batch_demand_forecasts.csv",
                    mime="text/csv",
                )
                
            else:
                st.warning("The API returned an empty response.")
                
        except requests.exceptions.ConnectionError:
            st.error(f"Failed to connect to the backend at `{API_URL}`. Is your Docker container currently running?")
        except Exception as e:
            st.error(f"An error occurred: {e}")