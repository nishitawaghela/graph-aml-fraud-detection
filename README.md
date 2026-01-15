 Graph-Based Anti-Money Laundering (AML) Detection System

## Project Overview
This project implements a graph-based approach to Anti-Money Laundering (AML) detection, addressing the limitations of traditional relational database systems in identifying complex financial fraud. By modeling transactions as a network graph, the system utilizes Graph Neural Networks (GNNs) and graph algorithms to detect structural anomalies indicative of money laundering, such as "Smurfing" (placement) and "Structuring" (layering).

The system features an end-to-end pipeline including synthetic data generation, graph database storage, automated algorithmic detection, machine learning classification, and an investigator dashboard.

## Key Features

### 1. Graph Data Engineering
* **Synthetic Data Generation:** A custom ETL pipeline generates realistic financial transaction data, including legit user behavior and specific money laundering topologies (Fan-Out/Fan-In patterns).
* **Noise Injection:** The system injects random transactional noise to simulate real-world data complexity and test model robustness.
* **Graph Modeling:** Data is modeled in Neo4j with `User` nodes and `TRANSACTION` edges, enabling efficient traversal and relationship analysis.

### 2. Graph Analytics & Algorithms
* **PageRank:** Utilized to identify high-centrality nodes acting as "money sinks" or shell companies.
* **Weakly Connected Components (WCC):** Applied to detect isolated sub-graphs and closed loops often associated with criminal rings.
* **Cypher Pattern Matching:** Automated queries designed to flag specific structural patterns (e.g., a single sender distributing funds to multiple intermediaries who funnel to a common recipient).

### 3. Machine Learning (Graph Neural Networks)
* **Model Architecture:** Implemented a Graph Convolutional Network (GCN) using PyTorch Geometric.
* **Feature Engineering:** Extracts topological features such as degree centrality and neighborhood aggregation.
* **Performance:** The model achieves approximately 93.5% accuracy in classifying illicit accounts based on network topology, demonstrating capability beyond simple rule-based heuristics.

### 4. Investigator Dashboard
* **Interactive Interface:** A Streamlit-based web application allowing analysts to query users and visualize transaction networks.
* **Real-Time Visualization:** Integrated PyVis to render interactive sub-graphs, highlighting suspicious connections and transaction flows.
* **Risk Metrics:** Displays calculated risk scores and transaction logs for individual entities.

## Technology Stack

* **Programming Language:** Python 3.9+
* **Graph Database:** Neo4j (via Bolt driver)
* **Machine Learning:** PyTorch, PyTorch Geometric, Scikit-learn
* **Web Framework:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Visualization:** PyVis
* **Data Simulation:** Faker

## Installation and Setup

### Prerequisites
* Python 3.9 or higher
* Neo4j Desktop (Active local database instance)
* Git

### 1. Clone the Repository
```bash
git clone [https://github.com/nishitawaghela/graph-aml-fraud-detection.git](https://github.com/nishitawaghela/graph-aml-fraud-detection.git)
cd graph-aml-fraud-detection

```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Database Configuration

Ensure your local Neo4j instance is running. Update the connection credentials in `src/data_generator.py`, `src/export_data.py`, and `src/app.py` if they differ from the defaults:

```python
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

```

## Usage Guide

### Step 1: Data Generation

Populate the graph database with synthetic users, transactions, and fraud patterns.

```bash
python src/data_generator.py

```

### Step 2: Feature Extraction and Training

Export graph features to CSV and train the Graph Neural Network.

```bash
python src/export_data.py
python src/train_gnn.py

```

### Step 3: Launch Dashboard

Start the web interface to explore the data and view detection results.

```bash
streamlit run src/app.py

```

## Project Structure

* **analysis/**: Contains Cypher queries for pattern matching and Graph Data Science (GDS) algorithms.
* **data/**: Stores intermediate CSV files for machine learning features.
* **src/**: Source code for the application.
* `data_generator.py`: ETL pipeline and data simulation.
* `export_data.py`: Script to extract features from Neo4j.
* `train_gnn.py`: GNN model definition and training loop.
* `app.py`: Streamlit dashboard application.


* **requirements.txt**: List of Python dependencies.

