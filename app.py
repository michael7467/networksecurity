import sys
import os

import certifi

from networksecurity.components import data_validation
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
ca=certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongodb_url=os.getenv("MONGODB_URL_KEY")
print(mongodb_url)

import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse, Response
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

client = pymongo.MongoClient(mongodb_url,tlsCAFile=ca)
from networksecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constants.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app=FastAPI()
origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")


@app.get("/",tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train",)
async def train(request:Request):
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training completed successfully.")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

@app.post("/predict",)
async def predict(request:Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)

        preprocessor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/final_model.pkl")
        network_model=NetworkModel(preprocessor=preprocessor,model=final_model)
        print(df.iloc[0])
        y_pred=network_model.predict(df)
        df['predicted_column']=y_pred   
        print(df["predicted_column"])
        df.to_csv("prediction_output/output.csv", index=False)
        table_html = df.to_html(classes="table table-striped")
        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={"request": request, "table": table_html}
        )
       
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

if __name__=="__main__":
    app_run(app, host="localhost", port=8000)
