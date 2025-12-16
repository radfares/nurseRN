# RAG Implementation Guide for nurseRN

## Overview
This guide provides step-by-step instructions for implementing a **Retrieval-Augmented Generation (RAG)** system in the **nurseRN** project. The goal is to enhance the project's ability to retrieve and synthesize clinical knowledge, improving the accuracy and reliability of the system.

## Prerequisites
Before starting, ensure you have the following:
- Python 3.8 or higher
- Required libraries: `pinecone-client`, `openai`, `tiktoken`, `tenacity`
- API keys for Pinecone and OpenAI

## Step 1: Set Up the Environment

### Install Required Libraries
```bash
pip install pinecone-client openai tiktoken tenacity
```

### Configure API Keys
Create a `.env` file in the project root and add your API keys:
```env
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
```

## Step 2: Implement the Vector Store

### Pinecone Vector Store
Replace the dummy `SimpleVectorStore` with a real Pinecone implementation.

**File: `vector_store.py`**
```python
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any

class PineconeVectorStore:
    def __init__(self, api_key: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

    def upsert(self, vectors: List[Dict[str, Any]], namespace: str) -> None:
        self.index.upsert(vectors=vectors, namespace=namespace)

    def query(self, query: str, namespace: str, top_k: int) -> List[Dict[str, Any]]:
        results = self.index.query(vector=query, namespace=namespace, top_k=top_k)
        return results["matches"]

    def clear_namespace(self, namespace: str) -> None:
        self.index.delete(delete_all=True, namespace=namespace)
```

## Step 3: Implement the Embedding Model

### OpenAI Embedding Model
Replace the dummy `SimpleEmbeddingModel` with a real OpenAI implementation.

**File: `embedding_model.py`**
```python
from openai import OpenAI
from typing import List

class OpenAIEmbeddingModel:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in response.data]
```

## Step 4: Implement the LLM

### OpenAI LLM
Replace the dummy `SimpleLLM` with a real OpenAI implementation.

**File: `llm.py`**
```python
from openai import OpenAI

class OpenAILLM:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
```

## Step 5: Implement the Data Ingestion Pipeline

### Clinical Data Ingestion Pipeline
Extend the `DataIngestionPipeline` to handle clinical data sources.

**File: `data_ingestion.py`**
```python
from typing import List, Dict, Any
import tiktoken

class ClinicalDataIngestionPipeline:
    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        tokens = self.tokenizer.encode(text)
        chunks = []
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks

    def ingest_clinical_data(self, data: str, namespace: str) -> None:
        chunks = self.chunk_text(data)
        embeddings = self.embedding_model.embed(chunks)
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vectors.append({
                "id": f"clinical_chunk_{i}",
                "values": embedding,
                "metadata": {"text": chunk, "source": "clinical_data"}
            })
        self.vector_store.upsert(vectors, namespace)
```

## Step 6: Implement the RAG Pipeline

### RAG Pipeline
Combine retrieval and generation into a single pipeline.

**File: `rag_pipeline.py`**
```python
from typing import List

class RAGPipeline:
    def __init__(self, vector_store, embedding_model, llm):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm

    def retrieve(self, query: str, namespace: str, top_k: int = 3) -> List[str]:
        embeddings = self.embedding_model.embed([query])
        results = self.vector_store.query(embeddings[0], namespace, top_k)
        return [result["metadata"]["text"] for result in results]

    def generate(self, query: str, namespace: str) -> str:
        context = self.retrieve(query, namespace)
        system_prompt = "You are a helpful clinical assistant."
        user_prompt = f"Context: {' '.join(context)}\n\nQuery: {query}"
        return self.llm.generate(system_prompt, user_prompt)
```

## Step 7: Integrate RAG into Agents

### Researcher Agent
Use RAG to retrieve factual knowledge from clinical databases.

**File: `agents/researcher.py`**
```python
from typing import List

class ResearcherAgent:
    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def retrieve_facts(self, query: str, namespace: str) -> List[str]:
        embeddings = self.embedding_model.embed([query])
        results = self.vector_store.query(embeddings[0], namespace, top_k=3)
        return [result["metadata"]["text"] for result in results]
```

### Validator Agent
Use RAG to fact-check claims against evidence.

**File: `agents/validator.py`**
```python
from typing import List

class ValidatorAgent:
    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def validate_claims(self, claim: str, namespace: str) -> bool:
        embeddings = self.embedding_model.embed([claim])
        results = self.vector_store.query(embeddings[0], namespace, top_k=3)
        # Implement validation logic here
        return True
```

### Clinician Agent
Use RAG to retrieve procedural knowledge (e.g., clinical protocols).

**File: `agents/clinician.py`**
```python
from typing import List

class ClinicianAgent:
    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def retrieve_protocols(self, query: str, namespace: str) -> List[str]:
        embeddings = self.embedding_model.embed([query])
        results = self.vector_store.query(embeddings[0], namespace, top_k=3)
        return [result["metadata"]["text"] for result in results]
```

## Step 8: Implement the Orchestrator

### Orchestrator
Coordinate the workflow between agents.

**File: `orchestrator.py`**
```python
from typing import Dict, Any

class Orchestrator:
    def __init__(self, vector_store, embedding_model, llm):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.llm = llm

    def orchestrate(self, query: str) -> str:
        # Retrieve facts
        researcher = ResearcherAgent(self.vector_store, self.embedding_model)
        facts = researcher.retrieve_facts(query, "knowledge")

        # Validate claims
        validator = ValidatorAgent(self.vector_store, self.embedding_model)
        is_valid = validator.validate_claims(query, "knowledge")

        # Retrieve protocols
        clinician = ClinicianAgent(self.vector_store, self.embedding_model)
        protocols = clinician.retrieve_protocols(query, "procedural")

        # Generate response
        system_prompt = "You are a helpful clinical assistant."
        user_prompt = f"Facts: {facts}\nProtocols: {protocols}\nQuery: {query}"
        return self.llm.generate(system_prompt, user_prompt)
```

## Step 9: Test the Implementation

### Test Cases
Create test cases to validate the RAG system.

**File: `tests/test_rag.py`**
```python
import unittest
from vector_store import PineconeVectorStore
from embedding_model import OpenAIEmbeddingModel
from llm import OpenAILLM
from agents.researcher import ResearcherAgent
from agents.validator import ValidatorAgent
from agents.clinician import ClinicianAgent

class TestRAGIntegration(unittest.TestCase):
    def setUp(self):
        self.vector_store = PineconeVectorStore("your_api_key", "nurseRN")
        self.embedding_model = OpenAIEmbeddingModel("your_api_key")
        self.llm = OpenAILLM("your_api_key")

    def test_retrieval(self):
        researcher = ResearcherAgent(self.vector_store, self.embedding_model)
        facts = researcher.retrieve_facts("What is the Eiffel Tower?", "knowledge")
        self.assertTrue(len(facts) > 0)

    def test_validation(self):
        validator = ValidatorAgent(self.vector_store, self.embedding_model)
        is_valid = validator.validate_claims("The Eiffel Tower is in Paris.", "knowledge")
        self.assertTrue(is_valid)

    def test_protocols(self):
        clinician = ClinicianAgent(self.vector_store, self.embedding_model)
        protocols = clinician.retrieve_protocols("How to treat a fever?", "procedural")
        self.assertTrue(len(protocols) > 0)

if __name__ == "__main__":
    unittest.main()
```

## Step 10: Deploy the System

### Deployment Steps
1. **Set Up Pinecone Index**: Create a Pinecone index for storing embeddings.
2. **Ingest Clinical Data**: Use the `ClinicalDataIngestionPipeline` to ingest clinical data.
3. **Run the Orchestrator**: Use the `Orchestrator` to coordinate the workflow between agents.
4. **Monitor and Validate**: Use the test cases to validate the system and monitor its performance.

## Conclusion
This guide provides a step-by-step approach to implementing a RAG system in the `nurseRN` project. By following these steps, you can enhance the project's ability to retrieve and synthesize clinical knowledge, improving the accuracy and reliability of the system.