import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.constants.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)

from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    def __init__(self, data_transformation_config: DataTransformationConfig,
                  data_validation_artifact: DataValidationArtifact):
        try:
            logging.info(f"{'>>'*20}Data Transformation log started.{'<<'*20}")
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def get_data_transformer_object(self) -> Pipeline:
        try:
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            preprocessing_obj: Pipeline = Pipeline(steps=[
                ("imputer", imputer)
            ])
            return preprocessing_obj
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("Starting data transformation.")
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)

            logging.info("Splitting input and target feature from training and testing dataframe.")
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)

            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            logging.info(f"Applying KNN Imputer to impute missing values in training and testing dataframe.")
            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transforremd_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transforremd_input_test_feature = preprocessor_object.transform(input_feature_test_df)
          
            train_arr = np.c_[transforremd_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transforremd_input_test_feature, np.array(target_feature_test_df)]
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,array= train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object
            )

            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path
            )
            
            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e