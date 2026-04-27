# 🏥 Clinical Insight Engine API

## Project Overview

The Clinical Insight Engine is an AI-powered decision-support system designed to analyze medical complaints—specifically focused on Dermatology. It uses BioClinicalBERT (a transformer-based NLP model) to understand complex medical descriptions and compare them against historical cases stored in MongoDB.

The system provides three key outputs for every query:

* **Suggested Resolution:** A predicted category and action plan based on past successes.
* **Confidence Score:** A mathematical reliability metric (0.0 to 1.0).
* **Analysis Explanation:** A human-readable breakdown of why the AI made that specific choice.

---

## 📂 Project Structure

To ensure the code runs correctly, organize your files as follows:

```
api/
  main.py                  # The FastAPI entry point where the server starts.

models/
  models.py               # Defines the data structure for requests and responses.

services/
  analyze_service.py      # Orchestrates the entire AI pipeline logic.

retrieval/
  database.py             # MongoDB connection and fetching.
  embedding.py            # BioClinicalBERT model implementation.
  retrieval_engine.py     # Cosine similarity search logic.

insight/
  confidence_engine.py    # Calculates the reliability score.
  insight_aggregator.py   # Weights the final resolution.
  explanation_generator.py # Creates the text summary.

config.py                 # Centralized settings (Database names, AI parameters like TOP_K).
utils.py                  # A migration tool to load initial data from CSV to MongoDB.
```

---

## 🛠️ Setup and Installation

### 1. Prerequisites

* Python 3.10+
* MongoDB: Ensure MongoDB is installed and running on localhost:27017.
* Dermatology Dataset: A CSV file (e.g., dermatology_cases.csv) containing historical case descriptions.

---

### 2. Install Dependencies

Open your terminal in the root folder and run:

```bash
pip install -r requirements.txt
```

---

### 3. Database Preparation 

Before the API can find "similar cases," you must load data into MongoDB:

* Ensure your CSV is in the root directory.

* Run the utility script to migrate data:

```bash
python utils.py
```

* Generate the AI embeddings (vectors) for the historical cases:

```bash
python -m retrieval.embedding_store
```

---

## 🚀 Running the API (The Demo)

### Step 1: Start the Server

Run the following command from the root directory:

```bash
python -m api.main
```

* API URL: http://localhost:8000
* Swagger UI (Interactive Docs): http://localhost:8000/docs

---

### Step 2: Sending a Request

You can use the provided simulation script or curl.

#### Sample JSON Payload:

```json
{
  "customer_id": "CUST-5582",
  "case_description": "Patient reports itchy red patches on the elbow that appear scaly.",
  "location": "Tamil Nadu",
  "category": "Skin Condition"
}
```

---

### Step 3: Automated Testing

To demonstrate the system's stability and error handling (Day 3 & 5 tasks), run:

```bash
python tests/test_api_simulation.py
```

---

## 💡 How the AI Works

* **Vectorization:** Your input text is converted into a 768-dimensional vector using the BioClinicalBERT model.

* **Retrieval:** The system calculates the Cosine Similarity between your query and every case in the database.

* **Scoring:** The Confidence Engine evaluates the results:

$$
Confidence = (0.75 \times \text{Similarity}) + (0.25 \times \text{Support Ratio})
$$

* **Aggregation:** The Insight Aggregator performs a weighted vote among the top 3 matches to decide the final suggested resolution.

---

## ⚠️ Error Handling

* **422 Unprocessable Entity:** Triggered if customer_id is missing or case_description is shorter than 10 characters.

* **404 Not Found:** Triggered if no similar cases are found in the database.

* **500 Internal Server Error:** Triggered if the AI model fails to load or the database is disconnected.
