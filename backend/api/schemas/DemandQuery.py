from pydantic import BaseModel

class ProductInfo(BaseModel):
  product_id: str
  current_stock_level: float
  unit_price_aed: float
  avg_sales_past_week:float
  sales_trend_std: float
  is_promotion_active: float
  upcoming_holiday_weekend: float