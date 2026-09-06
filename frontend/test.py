import json
import time
import requests
import pandas as pd
import streamlit as st
import os

# Replace with your live Render URL in production
api_url = os.getenv("API_URL")
endpoint = f"{api_url}/predict/expected-demand"

st.set_page_config(page_title="Demand Forecasting Studio", layout="wide")
st.header("📦 Unified Demand Forecasting Studio")
st.write("Execute high-speed demand forecasts and restock schedules via bulk file upload or real-time manual item entry.")

# Create two distinct workspace tabs
tab_batch, tab_manual = st.tabs(["📦 Batch File Upload", "📝 Manual Item Entry"])

# ==========================================
# TAB 1: HIGH-VOLUME BATCH FILE UPLOAD
# ==========================================
with tab_batch:
    uploaded_file = st.file_uploader(
        "Upload Inventory File (.txt, .json, or .csv with required model features)", 
        type=["txt", "json", "csv"],
        key="batch_uploader"
    )

    if uploaded_file is not None:
        try:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            
            # Fast format-specific parsing
            if file_ext in ["txt", "json"]:
                raw_content = uploaded_file.getvalue().decode("utf-8")
                payload = json.loads(raw_content)
                df_input = pd.DataFrame(payload)
            else:
                df_input = pd.read_csv(uploaded_file)
                payload = df_input.to_dict(orient="records")
            
            if "product_id" in df_input.columns:
                df_input["product_id"] = df_input["product_id"].astype(str).str.strip()
            else:
                st.error("❌ File is missing required attribute: 'product_id'")
                st.stop()
                
            st.subheader("1. Input Catalog Preview")
            st.write(f"Loaded **{len(df_input):,}** items from `{uploaded_file.name}`.")
            st.dataframe(df_input, use_container_width=True, height=200)
            
            if st.button(f"⚡ Execute Batch Forecast ({len(df_input):,} Items)", type="primary", key="btn_batch"):
                with st.spinner("Executing vectorized LightGBM inference..."):
                    start_time = time.time()
                    try:
                        response = requests.post(endpoint, json=payload, timeout=180)
                        round_trip_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            raw_data = response.json().get("predictions", {})
                            clean_data = {str(k).strip(): float(v) for k, v in raw_data.items()}
                            
                            df_results = df_input.copy()
                            df_results["Forecasted Weekly Demand"] = (
                                df_results["product_id"].map(clean_data).fillna(0).round(0).astype(int)
                            )
                            
                            if "current_stock_level" in df_results.columns:
                                df_results["Recommended Re-stock Amount"] = (
                                    df_results["Forecasted Weekly Demand"] - df_results["current_stock_level"]
                                ).clip(lower=0).astype(int)
                            
                            st.success("Batch processing complete! Logs written to PostgreSQL asynchronously.")
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Total Items Processed", f"{len(df_results):,}")
                            col2.metric("Round-Trip Time", f"{round_trip_time:.2f} s")
                            throughput = int(len(df_results) / round_trip_time) if round_trip_time > 0 else len(df_results)
                            col3.metric("Throughput Speed", f"{throughput:,} items/sec")
                            
                            st.subheader("2. Forecast & Restock Schedule")
                            st.dataframe(df_results, use_container_width=True, height=450)
                            
                            col_dl1, col_dl2 = st.columns(2)
                            with col_dl1:
                                st.download_button(
                                    label="📥 Download Results (CSV)",
                                    data=df_results.to_csv(index=False).encode('utf-8'),
                                    file_name=f"demand_forecast_{int(time.time())}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            with col_dl2:
                                st.download_button(
                                    label="📥 Download Results (JSON Array)",
                                    data=df_results.to_json(orient="records", indent=2).encode('utf-8'),
                                    file_name=f"demand_forecast_{int(time.time())}.json",
                                    mime="application/json",
                                    use_container_width=True
                                )
                        else:
                            st.error(f"API Error {response.status_code}: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Network error occurred: {e}")
        except Exception as e:
            st.error(f"Error processing file: {e}")


# ==========================================
# TAB 2: REAL-TIME MANUAL ITEM ENTRY
# ==========================================
with tab_manual:
    st.subheader("Enter SKU Attributes for Instant Forecast")
    
    # Using an st.form prevents the UI from reloading every time a user types a number
    with st.form("manual_entry_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_id = st.text_input("Product ID / SKU", value="SKU-9999")
            current_stock = st.number_input("Current Stock Level", min_value=0, value=15, step=1)
            unit_price = st.number_input("Unit Price (AED)", min_value=0.0, value=150.00, step=5.0)
            
        with col2:
            avg_sales = st.number_input("Avg Sales (Past Week)", min_value=0.0, value=85.5, step=1.0)
            sales_std = st.number_input("Sales Trend STD", min_value=0.0, value=12.4, step=0.5)
            
        with col3:
            is_promo = st.selectbox("Active Promotion?", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
            is_holiday = st.selectbox("Upcoming Holiday Weekend?", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
            
        submit_manual = st.form_submit_button("⚡ Predict Single SKU Demand", type="primary", use_container_width=True)
        
    if submit_manual:
        if not product_id.strip():
            st.warning("Please enter a valid Product ID.")
        else:
            # Package manual inputs into the exact dictionary structure expected by the API
            manual_payload = [{
                "product_id": product_id.strip(),
                "current_stock_level": int(current_stock),
                "unit_price_aed": float(unit_price),
                "avg_sales_past_week": float(avg_sales),
                "sales_trend_std": float(sales_std),
                "is_promotion_active": int(is_promo),
                "upcoming_holiday_weekend": int(is_holiday)
            }]
            
            with st.spinner(f"Forecasting demand for {product_id}..."):
                try:
                    # Reuse the exact same optimized batch endpoint by sending a 1-item list!
                    response = requests.post(endpoint, json=manual_payload, timeout=10)
                    
                    if response.status_code == 200:
                        raw_data = response.json().get("predictions", {})
                        clean_data = {str(k).strip(): float(v) for k, v in raw_data.items()}
                        
                        pred_value = clean_data.get(product_id.strip(), 0.0)
                        forecasted_demand = int(round(pred_value, 0))
                        restock_amount = max(0, forecasted_demand - int(current_stock))
                        
                        st.success(f"Forecast generated and logged to PostgreSQL for item **{product_id}**!")
                        
                        # High-impact visual metric display for single items
                        res_col1, res_col2, res_col3 = st.columns(3)
                        res_col1.metric("Current Stock Level", f"{current_stock:,} units")
                        res_col2.metric("Forecasted Weekly Demand", f"{forecasted_demand:,} units", delta=f"{forecasted_demand - current_stock} vs stock")
                        res_col3.metric("Recommended Restock", f"{restock_amount:,} units", delta_color="inverse" if restock_amount > 0 else "normal")
                        
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Network error occurred: {e}")