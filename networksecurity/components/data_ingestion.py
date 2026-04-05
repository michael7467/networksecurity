from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## cnonfiguration for data ingestion config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os,sys
import numpy as np
import pymongo
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'>>'*20} Data Ingestion {'<<'*20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def export_collection_as_dataframe(self):
        """
        Export data from MongoDB to pandas DataFrame
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            print(f"Connected to MongoDB at {MONGO_DB_URL}")
            print(f"Accessing database: {database_name}, collection: {collection_name}")
            collection = self.mongo_client[database_name][collection_name]
            print("Number of documents in collection:", collection.count_documents({}))
            df=pd.DataFrame(list(collection.find()))
            print(f"Exported data from MongoDB to DataFrame with shape: {df.shape}")
            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], axis=1, inplace=True)
           
            df.replace({"na": np.nan}, inplace=True )
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
   
    def export_data_into_feature_store(self, dataframe:pd.DataFrame):
        """
        Export data into feature store
        """
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def split_data_as_train_test(self, dataframe:pd.DataFrame):
        """
        Split data into train and test set
        """
        try:
           train_set, test_set = train_test_split(
               dataframe, test_size=self.data_ingestion_config.train_test_split_ratio, 
               )
           logging.info("Performed train test split on the dataframe")
           logging.info("Exited the split_data_as_train_test method of DataIngestion class")
           dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
           os.makedirs(dir_path, exist_ok=True)
           logging.info(f"Exporting training data to file: {self.data_ingestion_config.training_file_path}")
           train_set.to_csv(
               self.data_ingestion_config.training_file_path, index=False, header=True)    
           
           test_set.to_csv(
                self.data_ingestion_config.test_file_path, index=False, header=True)
           logging.info(f"Exporting testing data to file: {self.data_ingestion_config.test_file_path}")
           
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    def initiate_data_ingestion(self):
        """
        Initiate data ingestion process
        """
        try:
            dataframe = self.export_collection_as_dataframe()
            print(dataframe.head())
            dataframe = self.export_data_into_feature_store(dataframe)
            print("After feature store export:", dataframe.head())
            self.split_data_as_train_test(dataframe)
            dataingestionartifact=DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.test_file_path
            )

            return dataingestionartifact


        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        

        
    