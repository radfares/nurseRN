# RAG Integration Plan for nurseRN

## Overview
This document outlines the plan to integrate a **Retrieval-Augmented Generation (RAG)** system into the **nurseRN** project. The goal is to enhance the project's ability to retrieve and synthesize clinical knowledge, improving the accuracy and reliability of the system.

## Project Structure
The `nurseRN` project is located at `/Users/hdz_agents/Documents/nurseRN`. The key directories and files include:
- `agents/`: Specialized agents (e.g., Researcher, Validator, Clinician).
- `data/`: Datasets and knowledge bases.
- `docs/`: Documentation and guides.
- `src/`: Core source code.
- `scripts/`: Utility scripts.
- `tests/`: Test cases.

## Integration Steps

### 1. Replace Dummy Components with Real Implementations

#### Vector Store
Replace `SimpleVectorStore` with **Pinecone** or **FAISS**.

**Example Implementation (Pinecone):**
```python
from pinecone import Pinecone, ServerlessSpec

class PineconeVectorStore(VectorStore):
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

#### Embedding Model
Replace `SimpleEmbeddingModel` with **OpenAI's `text-embedding-3-small`** or **Hugging Face's sentence transformers**.

**Example Implementation (OpenAI):**
```python
from openai import OpenAI

class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in response.data]
```

#### LLM
Replace `SimpleLLM` with **OpenAI's GPT-3.5/4**, **Mistral**, or **Claude**.

**Example Implementation (OpenAI):**
```python
class OpenAILLM(LLM):
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

### 2. Integrate RAG into Existing Agents

#### Researcher Agent
Use RAG to retrieve factual knowledge from clinical databases (e.g., PubMed, clinical guidelines).

**Example Integration:**
```python
class ResearcherAgent:
    def __init__(self, vector_store: VectorStore, embedding_model: EmbeddingModel):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def retrieve_facts(self, query: str, namespace: str) -> List[str]:
        embeddings = self.embedding_model.embed([query])
        results = self.vector_store.query(embeddings[0], namespace, top_k=3)
        return [result["metadata"]["text"] for result in results]
```

#### Validator Agent
Use RAG to fact-check claims against evidence.

**Example Integration:**
```python
class ValidatorAgent:
    def __init__(self, vector_store: VectorStore, embedding_model: EmbeddingModel):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def validate_claims(self, claim: str, namespace: str) -> bool:
        embeddings = self.embedding_model.embed([claim])
        results = self.vector_store.query(embeddings[0], namespace, top_k=3)
        # Implement validation logic here
        return True
```

#### Clinician Agent
Use RAG to retrieve procedural knowledge (e.g., clinical protocols).

**Example Integration:**
```python
class ClinicianAgent:
    def __init__(self, vector_store: VectorStore, embedding_model: EmbeddingModel):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def retrieve_protocols(self, query: str, namespace: str) -> List[str]:
        embeddings = self.embedding_model.embed([query])
        results = self.vector_store.query(embeddings[0], namespace, top_k=3)
        return [result["metadata"]["text"] for result in results]
```

### 3. Implement MCP for Structured Communication

Use the `context_manager.py` to standardize communication between agents.

**Example Implementation:**
```python
from context_manager import create_mcp_message

class Orchestrator:
    def __init__(self, vector_store: VectorStore, embedding_model: EmbeddingModel, llm: LLM):
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

### 4. Extend Data Ingestion Pipeline

Modify `DataIngestionPipeline` to handle clinical data sources (e.g., PDFs, CSV files, APIs).

**Example Implementation:**
```python
class ClinicalDataIngestionPipeline(DataIngestionPipeline):
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

### 5. Test and Validate

Use the `tests/` directory to validate the RAG system.

**Example Test Case:**
```python
import unittest

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

## Next Steps

1. **Replace Dummy Components**: Start with `VectorStore`, `EmbeddingModel`, and `LLM`.
2. **Integrate RAG into Agents**: Update the Researcher, Validator, and Clinician agents.
3. **Test and Validate**: Ensure the system works with real clinical data.

## Conclusion
This plan outlines the steps to integrate a RAG system into the `nurseRN` project. By following these steps, you can enhance the project's ability to retrieve and synthesize clinical knowledge, improving the accuracy and reliability of the system.