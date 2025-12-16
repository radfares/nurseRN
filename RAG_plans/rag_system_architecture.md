# RAG System Architecture for nurseRN

## Overview
This document outlines the **architecture** of the **Retrieval-Augmented Generation (RAG)** system for the **nurseRN** project. The architecture is designed to be **modular, scalable, and adaptable**, allowing for easy integration into the existing `nurseRN` project and future extensions.

## Architecture Diagram

```plaintext
+---------------------+       +---------------------+       +---------------------+
|                     |       |                     |       |                     |
|   Researcher Agent  |------>|   Validator Agent   |------>|   Clinician Agent   |
|                     |       |                     |       |                     |
+---------------------+       +---------------------+       +---------------------+
       ^                             ^                             ^
       |                             |                             |
       v                             v                             v
+---------------------+       +---------------------+       +---------------------+
|                     |       |                     |       |                     |
|   Vector Store      |       |   Embedding Model   |       |   LLM               |
|   (Pinecone/FAISS)  |       |   (OpenAI/Hugging   |       |   (OpenAI/Mistral/  |
|                     |       |   Face)             |       |   Claude)           |
+---------------------+       +---------------------+       +---------------------+
       ^                             ^                             ^
       |                             |                             |
       v                             v                             v
+---------------------+       +---------------------+       +---------------------+
|                     |       |                     |       |                     |
|   Data Ingestion    |       |   RAG Pipeline      |       |   Orchestrator      |
|   Pipeline          |       |                     |       |                     |
+---------------------+       +---------------------+       +---------------------+
```

## Components

### 1. Vector Store
**Purpose**: Store and retrieve embeddings for clinical data.
**Options**: Pinecone, FAISS, Weaviate.
**Implementation**: `PineconeVectorStore` (see `vector_store.py`).

### 2. Embedding Model
**Purpose**: Generate embeddings for text data.
**Options**: OpenAI's `text-embedding-3-small`, Hugging Face's sentence transformers.
**Implementation**: `OpenAIEmbeddingModel` (see `embedding_model.py`).

### 3. LLM
**Purpose**: Generate text based on retrieved context.
**Options**: OpenAI's GPT-3.5/4, Mistral, Claude.
**Implementation**: `OpenAILLM` (see `llm.py`).

### 4. Data Ingestion Pipeline
**Purpose**: Ingest and process clinical data into the vector store.
**Implementation**: `ClinicalDataIngestionPipeline` (see `data_ingestion.py`).

### 5. RAG Pipeline
**Purpose**: Combine retrieval and generation into a single pipeline.
**Implementation**: `RAGPipeline` (see `rag_pipeline.py`).

### 6. Agents
**Purpose**: Specialized agents for different tasks.
**Implementations**:
- `ResearcherAgent` (see `agents/researcher.py`).
- `ValidatorAgent` (see `agents/validator.py`).
- `ClinicianAgent` (see `agents/clinician.py`).

### 7. Orchestrator
**Purpose**: Coordinate the workflow between agents.
**Implementation**: `Orchestrator` (see `orchestrator.py`).

## Data Flow

### 1. Data Ingestion
1. **Input**: Clinical data (e.g., PubMed articles, clinical guidelines).
2. **Process**:
   - Chunk the data into smaller pieces.
   - Generate embeddings for each chunk.
   - Store embeddings in the vector store.
3. **Output**: Embeddings stored in the vector store.

### 2. Retrieval
1. **Input**: Query (e.g., "What is the treatment for diabetes?").
2. **Process**:
   - Generate embeddings for the query.
   - Retrieve similar embeddings from the vector store.
   - Extract the corresponding text chunks.
3. **Output**: Retrieved text chunks.

### 3. Generation
1. **Input**: Retrieved text chunks and query.
2. **Process**:
   - Generate a response using the LLM.
   - Use the retrieved text chunks as context.
3. **Output**: Generated response.

### 4. Orchestration
1. **Input**: Query.
2. **Process**:
   - Retrieve facts using the Researcher Agent.
   - Validate claims using the Validator Agent.
   - Retrieve protocols using the Clinician Agent.
   - Generate a response using the LLM.
3. **Output**: Final response.

## Implementation Details

### Vector Store
**PineconeVectorStore**:
- **Upsert**: Store vectors in the vector store.
- **Query**: Retrieve similar vectors from the vector store.
- **Clear Namespace**: Clear all vectors in a namespace.

### Embedding Model
**OpenAIEmbeddingModel**:
- **Embed**: Generate embeddings for a list of texts.

### LLM
**OpenAILLM**:
- **Generate**: Generate text using the LLM.

### Data Ingestion Pipeline
**ClinicalDataIngestionPipeline**:
- **Chunk Text**: Chunk text into smaller pieces.
- **Ingest Clinical Data**: Ingest clinical data into the vector store.

### RAG Pipeline
**RAGPipeline**:
- **Retrieve**: Retrieve relevant text chunks from the vector store.
- **Generate**: Generate a response using the LLM.

### Agents
**ResearcherAgent**:
- **Retrieve Facts**: Retrieve factual knowledge from clinical databases.

**ValidatorAgent**:
- **Validate Claims**: Fact-check claims against evidence.

**ClinicianAgent**:
- **Retrieve Protocols**: Retrieve procedural knowledge (e.g., clinical protocols).

### Orchestrator
**Orchestrator**:
- **Orchestrate**: Coordinate the workflow between agents.

## Testing

### Test Cases
1. **Retrieval Test**: Test the retrieval of factual knowledge.
2. **Validation Test**: Test the validation of claims.
3. **Protocols Test**: Test the retrieval of procedural knowledge.
4. **Generation Test**: Test the generation of responses.
5. **Orchestration Test**: Test the coordination between agents.

### Test Implementation
**File**: `tests/test_rag.py`
- **Test Retrieval**: Test the retrieval of factual knowledge.
- **Test Validation**: Test the validation of claims.
- **Test Protocols**: Test the retrieval of procedural knowledge.

## Deployment

### Deployment Steps
1. **Set Up Pinecone Index**: Create a Pinecone index for storing embeddings.
2. **Ingest Clinical Data**: Use the `ClinicalDataIngestionPipeline` to ingest clinical data.
3. **Run the Orchestrator**: Use the `Orchestrator` to coordinate the workflow between agents.
4. **Monitor and Validate**: Use the test cases to validate the system and monitor its performance.

## Conclusion
This document outlines the **architecture** of the **RAG system** for the **nurseRN** project. The architecture is designed to be **modular, scalable, and adaptable**, allowing for easy integration into the existing `nurseRN` project and future extensions. By following this architecture, you can enhance the project's ability to retrieve and synthesize clinical knowledge, improving the accuracy and reliability of the system.