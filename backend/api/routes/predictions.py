import pickle

from pathlib import Path
import pandas as pd
from fastapi import APIRouter, BackgroundTasks
from schemas.DemandQuery import ProductInfo
from routes.background_logging_task import log_prediction_into_db



# Importing ML model
current_dir = Path(__file__).resolve().parent
path_to_model = current_dir.parent.parent / "model" / "best_model.pkl"
with open(path_to_model, 'rb') as file:
     model = pickle.load(file)
model.set_params(verbosity=-1)


router = APIRouter(prefix="/predict")

@router.post('/expected-demand')
def prediction(payload: list[ProductInfo], loggging_task: BackgroundTasks):
    data = pd.DataFrame([product.model_dump() for product in payload])

    product_ids = data["product_id"]

    features = data.drop(columns=['product_id'])
    forcasted_demand = model.predict(features).tolist()

    loggging_task.add_task(log_prediction_into_db, product_ids, forcasted_demand)

    return {"predictions": dict(zip(product_ids, forcasted_demand))}
