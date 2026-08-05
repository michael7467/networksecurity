from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.utils.class_weight import compute_sample_weight
import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import sys,os
import numpy as np
#import dill
import pickle


def read_yaml_file(file_path:str)->dict:
    try:
        with open(file_path, 'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path:str,content:object,replace:bool=False)->None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as yaml_file:
            yaml.dump(content, yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_numpy_array_data(file_path:str,array:np.array)->None:
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def save_object(file_path:str,obj:object)->None:
    try:
        logging.info("Entered the save_object method of MainUtils class")
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def load_object(file_path:str)->object:
    try:
        if not os.path.exists(file_path):
            raise NetworkSecurityException(f"The file: {file_path} is not exists")
        logging.info("Entered the load_object method of MainUtils class")
        with open(file_path, 'rb') as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def load_numpy_array_data(file_path:str)->np.array:
    try:
        with open(file_path, 'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def evaluate_models(X_train,y_train,X_test,y_test,models:dict,params:dict)->dict:
    try:
        report = {}
        sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)
        for i in range(len(models)):
            model = list(models.values())[i]
            para = params[list(models.keys())[i]]

            # Models that expose class_weight already balance themselves at construction time.
            # Models that don't (Gradient Boosting, AdaBoost) get it via sample_weight instead,
            # so every model ends up class-balanced one way or the other.
            if "class_weight" in model.get_params():
                fit_kwargs = {}
            else:
                fit_kwargs = {"sample_weight": sample_weight}

            gs = GridSearchCV(model,para,cv=3,scoring="f1")
            gs.fit(X_train,y_train,**fit_kwargs)
            model.set_params(**gs.best_params_)
            model.fit(X_train,y_train,**fit_kwargs)
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            train_model_score = f1_score(y_true=y_train, y_pred=y_train_pred)
            test_model_score = f1_score(y_true=y_test, y_pred=y_test_pred)
            logging.info(
                f"{list(models.keys())[i]}: cv_f1={gs.best_score_:.4f} "
                f"train_f1={train_model_score:.4f} test_f1={test_model_score:.4f}"
            )
            # Model comparison uses the cross-validated score (mean f1 across the cv folds
            # for the winning hyperparameters), not the single train/test split score above —
            # a single split can make a model look better or worse than it consistently is.
            report[list(models.keys())[i]] = gs.best_score_
        return report
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e