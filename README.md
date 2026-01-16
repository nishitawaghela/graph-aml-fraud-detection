# Technical Case Study: Graph-Based Anti-Money Laundering (AML) Detection System

**Author:** Nishita Waghela

**Date:** 16th January 2026

**Project Type:** End-to-End Data Science & Engineering

**Deployment:** https://graph-aml-fraud-detection-6ffm6yydeuhi4tyq8xr5du.streamlit.app/

---

## 1. Executive Summary

Financial crime is evolving rapidly, with illicit actors utilizing sophisticated obfuscation techniques such as **Smurfing** (structuring) and **Layering** to evade detection. Traditional Anti-Money Laundering (AML) systems, predicated on relational databases and static rule-based heuristics (e.g., "flag transactions > $10,000"), suffer from high false-negative rates due to their inability to natively analyze complex relationship topologies.

This project implements a **Graph-Based Fraud Detection System** utilizing **Graph Neural Networks (GNNs)**. By shifting the data paradigm from tabular rows to a high-dimensional property graph, the system identifies structural anomalies in transaction networks with **93.5% classification accuracy**. The solution features a full-stack pipeline, including a synthetic simulation engine, a graph-native persistence layer, and a deployed forensic dashboard for real-time investigative auditing.

---

## 2. Problem Statement

Current banking compliance infrastructure faces three distinct engineering challenges:

1. **Topological Blindness:** Relational databases (SQL) treat customers as independent instances. They fail to capture **homophily**—the tendency of fraudulent accounts to cluster together—and distinct topologies like **Fan-Out** (Placement) and **Fan-In** (Integration).
2. **The "Join" Penalty:** Analyzing multi-hop transaction paths (e.g., A  B  C  D) in SQL requires computationally expensive recursive JOINS, which degrade performance exponentially.
3. **Adversarial Adaptation:** Criminals engage in "Structuring," deliberately keeping transaction values below reporting thresholds to bypass scalar filters.

---

## 3. Proposed Solution

This solution leverages **Graph Theory** and **Geometric Deep Learning** to detect fraud based on connectivity rather than just magnitude.

* **Graph Data Modeling:** Entities and transactions are modeled as a **Directed Property Graph**, allowing for  index-free adjacency traversals.
* **Graph Convolutional Networks (GCN):** A semi-supervised deep learning model that utilizes **neural message passing** to aggregate information from a node's local neighborhood, effectively "learning" the shape of money laundering rings.
* **Interactive Forensics:** A stateless visualization layer that renders sub-graph isomorphisms, enabling analysts to visually verify "Smurfing" chains.

---

## 4. Technology Stack

I selected a modern, Python-centric stack optimized for Graph Machine Learning and rapid prototyping.

* **Language:** Python 3.9+
* **Graph Database:** Neo4j (Cypher Query Language)
* **Deep Learning:** PyTorch, PyTorch Geometric (GNNs)
* **Data Engineering:** Pandas, Faker (Synthetic Data Generation)
* **Visualization:** PyVis (Network Visualization), Streamlit (Frontend)
* **Deployment:** Streamlit Cloud (Stateless Architecture)

---

## 5. Technical Methodology

My approach followed a rigorous Data Science lifecycle, adapted specifically for Graph Machine Learning.

### A. Data Engineering & ETL (The Simulation Engine)

Since real-world banking datasets are protected by privacy laws (PII), I engineered a custom **Synthetic Data Pipeline** to generate high-fidelity transaction logs.

* **Stochastic Topology Injection:** Instead of random noise, I programmed the pipeline to inject specific graph structures that mirror known money laundering typologies:
* *The "Smurfing" Pattern (Placement):* A single source node distributes funds to  intermediate nodes (Mules).
* *The "Shell Company" Pattern (Integration):* Those  Mules funnel funds into a single high-degree target node.


* **Noise Augmentation:** To prevent model overfitting, I injected random background noise (legitimate retail transactions) using probabilistic edge creation. This forced the AI to distinguish between "dense legitimate hubs" (like Amazon) and "dense criminal hubs" (like a Shell Company).

### B. Graph Analytics & Feature Extraction

Before applying Deep Learning, I utilized deterministic graph algorithms to extract topological feature vectors from the raw network:

* **PageRank Centrality:** Used to identify "Sink Nodes"—accounts that receive disproportionate amounts of flow but rarely send money out.
* **Weakly Connected Components (WCC):** Used to partition the massive graph into disjoint subgraphs, isolating "closed loops" often indicative of wash trading.

### C. Geometric Deep Learning (The GNN)

I chose a **Graph Convolutional Network (GCN)** because it respects the *relational independence* of the data.

* **Architecture:** A 2-layer GCN implemented in **PyTorch Geometric**.
* **Message Passing Mechanism:** The model uses "Neural Message Passing." For every user, it aggregates the feature vectors of their direct neighbors (1-hop) and their neighbors' neighbors (2-hop).
* **Intuition:** This allows the model to "see" that a user is suspicious not because *they* did something wrong, but because they are receiving funds from a known high-risk Mule.
* **Result:** The model converged at **93.5% Test Accuracy**, successfully classifying nodes into *Normal*, *Mule*, and *Launderer* classes.

---

## 6. Engineering Challenges & Solutions

Building a graph-native application came with unique hurdles. Here is how I overcame them.

### Challenge 1: The "Cloud Connectivity" Bottleneck

* **The Issue:** I initially planned to connect the Streamlit app to a live Neo4j AuraDB cloud instance. However, this introduced significant query latency and reliability issues (free-tier instances pausing after inactivity).
* **The Fix:** I re-architected the application to use a **Stateless In-Memory Architecture**. Instead of maintaining a persistent database connection, the app utilizes Python's **Session State** to instantiate the graph data structure entirely in the server's RAM. This reduced query latency to near-zero and guaranteed 100% uptime for the demo.

### Challenge 2: "It Works on My Machine" (Dependency Management)

* **The Issue:** The application ran perfectly locally but crashed on Streamlit Cloud with `ModuleNotFoundError`. The cloud environment did not recognize the specific graph libraries I was using.
* **The Fix:** I performed a rigorous dependency audit. I configured a `requirements.txt` file to explicitly version-lock libraries like `pyvis`, `networkx`, and `torch_geometric`, ensuring the cloud build environment mirrored my local development environment exactly.

### Challenge 3: Visualizing High-Dimensional Networks

* **The Issue:** Attempting to render the entire dataset (10,000+ nodes) crashed the frontend browser due to DOM overload.
* **The Fix:** I implemented **Local Subgraph Sampling** (k-Hop Queries). The dashboard now dynamically queries and renders only the "k=2" neighborhood of the target node. This keeps the visualization lightweight and responsive while providing necessary context.

---

## 7. Project Limitations

To ensure transparency regarding the system's capabilities:

1. **Synthetic Data:** The model was trained on generated data. Real-world financial data contains significantly more noise and class imbalance, which would likely require retraining and hyperparameter tuning.
2. **Scalability:** The current in-memory deployment strategy works for demonstrations but is bounded by server RAM. A production implementation would require a distributed graph processing framework like **Apache Spark GraphX**.
3. **Static Analysis:** The model analyzes a static snapshot of the transaction graph. It does not currently account for temporal dynamics (e.g., high-frequency trading bursts).

