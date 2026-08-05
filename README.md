# Network Security: Phishing Detection Pipeline

An end-to-end machine learning pipeline for detecting phishing/malicious network traffic, built as a modular, production-style MLOps project — covering data ingestion, validation, transformation, model training, and deployment as a served API.

## Pipeline

The training pipeline runs as a sequence of independently configured, testable stages, each producing a versioned artifact consumed by the next:

1. **Data Ingestion** — pulls source data from MongoDB Atlas.
2. **Data Validation** — schema validation against an expected column/type definition (`data_schema/`), with drift detection between the current dataset and a reference distribution.
3. **Data Transformation** — preprocessing via scikit-learn, including `KNNImputer` for missing values and `RobustScaler` for outlier-resistant feature scaling; transformation objects are serialized for reuse at inference time.
4. **Model Training** — trains the final classifier, with experiment tracking via MLflow (hosted on DagsHub) capturing parameters, metrics, and model artifacts across runs.

## Serving

A FastAPI application exposes the trained pipeline:

- `GET /train` — triggers a full pipeline run on demand.
- `POST /predict` — accepts a CSV upload, runs it through the saved preprocessing + model artifacts, and returns predictions as a rendered HTML table.
- `GET /docs` — interactive API documentation (Swagger UI).

## Infrastructure

- **Containerization:** Docker.
- **CI/CD:** GitHub Actions, automating build and deployment on push.
- **Data storage:** MongoDB Atlas.
- **Experiment tracking:** MLflow via DagsHub.

## Tech Stack

Python · FastAPI · scikit-learn · MLflow · DagsHub · MongoDB Atlas (PyMongo) · Docker · GitHub Actions

## Project Structure
networksecurity/
├── networksecurity/ # Core package: pipeline components, entities, utils
├── data_schema/ # Expected schema definition for validation
├── final_model/ # Serialized preprocessor + trained model
├── valid_data/ # Validated data output
├── prediction_output/ # Batch prediction results
├── templates/ # HTML templates for the /predict view
├── main.py # Runs the full training pipeline
├── app.py # FastAPI serving application
├── push_data.py # Loads source data into MongoDB
└── Dockerfile

## Running Locally

```bash
pip install -r requirements.txt
python main.py        # run the training pipeline
python app.py          # start the API server (http://localhost:8080)
```

Requires a `.env` file with a `MONGO_DB_URL` variable pointing to your MongoDB Atlas connection string.