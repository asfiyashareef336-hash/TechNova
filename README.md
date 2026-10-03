# Agentic GraphRAG

An intelligent question-answering system that compares **RAG, GraphRAG, and Agentic GraphRAG** using semantic search, TigerGraph, evidence evaluation, and LLM-based reasoning.

## 🚀 Overview

This project was developed for the **TigerGraph Agentic GraphRAG Hackathon **.

The system answers questions using three different approaches:

* **RAG** – retrieves relevant documents using vector similarity search.
* **GraphRAG** – combines vector search with TigerGraph-based graph traversal.
* **Agentic GraphRAG** – uses an agent state, orchestrator, retrieval, graph exploration, evidence evaluation, and LLM reasoning to investigate questions.

The system also records an **agentic trace** showing the investigation steps, retrieved documents, tokens used, operation time, and stopping reason.

## 🏗️ Architecture

### Main Components

1. **User Question**
2. **Agent Harness / Orchestrator**
3. **Vector Search**
4. **TigerGraph Knowledge Graph**
5. **Evidence Evaluation**
6. **LLM Answer Generation**
7. **Agentic Trace and Metrics**

### Technologies

* Python
* Streamlit
* Sentence Transformers
* NumPy
* TigerGraph
* pyTigerGraph
* Groq API
* GPT-OSS-120B
* Wikipedia Corpus

## 🔄 Three Pipelines

### 1. RAG

```text
Question
   ↓
Vector Search
   ↓
Evidence Evaluation
   ↓
LLM
   ↓
Answer
```

### 2. GraphRAG

```text
Question
   ↓
Vector Search
   ↓
TigerGraph Traversal
   ↓
Evidence Evaluation
   ↓
LLM
   ↓
Answer
```

### 3. Agentic GraphRAG

```text
Question
   ↓
Agent Orchestrator
   ↓
Choose Investigation Action
   ↓
Vector Search / Graph Search
   ↓
Evidence Evaluation
   ↓
LLM Answer
   ↓
Agentic Trace
```

## 📊 Benchmark Results

The system was evaluated on **100 visible evaluation questions**.

| Pipeline         | Accuracy | Completeness | Avg. Tokens |
| ---------------- | -------: | -----------: | ----------: |
| RAG              |    74.0% |       49.01% |        2943 |
| GraphRAG         |    76.0% |       51.55% |        2818 |
| Agentic GraphRAG |    76.0% |       53.16% |        2630 |

The benchmark compares the three approaches using accuracy, completeness, and token efficiency.

## 🔎 Agentic Trace

For each Agentic GraphRAG investigation, the system records:

* Investigation steps
* Actions selected by the agent
* Retrieved documents
* Evidence evaluation
* Tokens used
* Operation time
* LLM generation time
* Total tokens
* Stopping reason

This provides visibility into how the agent investigates and reaches its answer.

## 🗄️ Knowledge Graph

The TigerGraph database contains:

* **2,951 Document vertices**
* **14,289 RelatedTo relationships**

The graph is used by GraphRAG and Agentic GraphRAG to explore relationships between documents.



## 🔐 Environment Variables

Create a local `.env` file containing your credentials:

```text
GROQ_API_KEY=your_groq_api_key
TIGERGRAPH_SECRET=your_tigergraph_secret
```

**Do not commit `.env` to GitHub.**

The repository uses `.gitignore` to exclude credentials and local environment files.

## ▶️ Running the Project

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

The application provides:

* RAG answer
* GraphRAG answer
* Agentic GraphRAG answer
* Evidence sources
* Agent actions
* Agentic trace
* Token usage
* Operation timing
* Stopping reason
* Retrieval metrics

## 🎯 Hackathon Deliverables

* Working Agentic GraphRAG system
* RAG, GraphRAG, and Agentic GraphRAG pipelines
* TigerGraph knowledge graph
* Agentic investigation trace
* Benchmark and metrics dashboard
* Architecture diagram
* Demo video
* GitHub repository

## 👩‍💻 Project

**Agentic GraphRAG – TigerGraph Hackathon **

Built using Python, Streamlit, TigerGraph, Sentence Transformers, and Groq LLM.

