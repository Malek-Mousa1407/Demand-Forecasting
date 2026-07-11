import math
import pickle
import logging
import warnings
from pathlib import Path
import sys
from fastapi import APIRouter
from schemas.DemandQuery import ProductInfo


# Importing Database Connection and Schema
backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))
from database.database_config import SessionLocal
import database.models as logging_table


# Setting up logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning)


# Importing ML model
current_dir = Path(__file__).resolve().parent
path_to_model = current_dir.parent.parent / "model" / "best_model.pkl"
with open(path_to_model, 'rb') as file:
     model = pickle.load(file)
model.set_params(verbosity=-1)


router = APIRouter(prefix="/predict")


@router.post('/expected-demand')
def prediction(products: list[ProductInfo]):
    
    total_forcast = []
    logs = []

    for product in products:
        features = list(product.model_dump(exclude={"product_id"}).values())

        logger.info(f"Prediction requested for Item IDs: {product.product_id}")

        prediction = model.predict([features])[0]

        forcasted_demand = int(math.ceil(prediction))

        re_order_amount = max(0, forcasted_demand - product.current_stock_level)

        total_forcast.append(
            {
                "Product Info": product,
                "Forecasted Weekly Demand": forcasted_demand,
                "Recommended Re-stock Amount": re_order_amount 
            })
        
        logs.append(
            logging_table.PredictionLog(
                item_id = str(product.product_id),
                prediction_value = forcasted_demand
            )
        )
    # Writing the logs to the DB
    try:
        db = SessionLocal()
        db.add_all(logs)
        db.commit()

    except Exception as e:
        print("Error in writing logs to DB.")
        db.rollback()

    return total_forcast