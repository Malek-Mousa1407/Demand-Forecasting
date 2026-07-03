import math

import pickle
import logging
import warnings

from pathlib import Path
from fastapi import APIRouter
from schemas.DemandQuery import ProductInfo


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning)


current_dir = Path(__file__).resolve().parent
path_to_model = current_dir.parent.parent / "model" / "best_model.pkl"

with open(path_to_model, 'rb') as file:
     model = pickle.load(file)
model.set_params(verbosity=-1)



router = APIRouter(prefix="/predict")

@router.post('/expected-demand')
def prediction(product: ProductInfo):
    features = list(product.model_dump(exclude={"product_id"}).values())
    prediction = model.predict([features], verbose = -1)[0]

    forcatsed_demand = int(math.ceil(prediction))

    re_order_amount = max(0, forcatsed_demand - product.current_stock_level)
    
    return {
        "Product Info": product,
        "Forecasted Weekly Demand": forcatsed_demand,
        "Recommended Re-stock Amount": re_order_amount 
    }



@router.post('/expected-demand-many')
def prediction(products: list[ProductInfo]):
    
    total_forcast = []

    for product in products:
        features = list(product.model_dump(exclude={"product_id"}).values())

        logger.info(f"Prediction requested for Item IDs: {product.product_id}")

        prediction = model.predict([features])[0]

        forcatsed_demand = int(math.ceil(prediction))

        re_order_amount = max(0, forcatsed_demand - product.current_stock_level)

        total_forcast.append(
            {
                "Product Info": product,
                "Forecasted Weekly Demand": forcatsed_demand,
                "Recommended Re-stock Amount": re_order_amount 
            })

    return total_forcast