from fastapi import FastAPI, Request
import time
from routes.predictions import router as predictions_router


api = FastAPI()


@api.get('/')
def prediction():
    return {"Status": "1"}


@api.middleware("http")
async def add_process_time_header(request: Request, call_next):

    if request.method == "POST" and "/predict" in str(request.url.path):
        start_time = time.time()

    response = await call_next(request)
    
    if request.method == "POST" and "/predict" in str(request.url.path):
        process_time = time.time() - start_time
        response.headers["X-Predicton-Time"] = str(process_time)
    
    return response



api.include_router(predictions_router)