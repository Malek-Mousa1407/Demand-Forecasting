import pickle
import math
from pathlib import Path
from fastapi import APIRouter
from schemas.DemandQuery import ProductInfo


# For local running
current_dir = Path(__file__).resolve().parent
path_to_model = current_dir.parent.parent / "model" / "best_model.pkl"
with open(path_to_model, 'rb') as file:
     model = pickle.load(file)


#  For docker
# path_to_model = Path("/app/model/best_model.pkl")
# with open(path_to_model, 'rb') as file:
#     model = pickle.load(file)


router = APIRouter(prefix="/predict")

@router.post('/expected-demand')
def prediction(product: ProductInfo):
    features = list(product.model_dump(exclude={"product_id"}).values())
    prediction = model.predict([features])[0]

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