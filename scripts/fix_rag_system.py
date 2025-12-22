#!/usr/bin/env python3
"""
RAG System Rescue Script
Diagnoses and fixes issues where files exist but are not retrievable.

Steps:
1. Validates environment (OPENAI_API_KEY)
2. Walks data/personal_library/indexed recursivley
3. Re-ingests all files with correct metadata
4. Runs verification search to confirm >5 documents retrievable

Usage:
    python scripts/fix_rag_system.py
"""

import os
import sys
import logging
from pathlib import Path
from typing import List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("rag_rescue")

# Import knowledge components
try:
    from src.knowledge.ingestion_service import KnowledgeIngestionService, IngestionResult
    from src.knowledge.vector_store import get_personal_library_store
    from src.knowledge.config import get_config
except ImportError as e:
    logger.error(f"Failed to import knowledge components: {e}")
    sys.exit(1)


def check_environment():
    """Verify essential environment variables."""
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY not found in environment")
        logger.info("Please set OPENAI_API_KEY and try again")
        sys.exit(1)
    logger.info("✅ Environment verified")


def scan_files(base_dir: Path) -> List[Path]:
    """recursively find all supported files."""
    if not base_dir.exists():
        logger.error(f"❌ Directory not found: {base_dir}")
        return []

    supported_exts = {".pdf", ".docx", ".txt", ".md"}
    files = []
    
    logger.info(f"Scanning {base_dir}...")
    
    for path in base_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in supported_exts:
            files.append(path)
            
    logger.info(f"✅ Found {len(files)} supported files on disk")
    return files


def reingest_files(service: KnowledgeIngestionService, files: List[Path]):
    """Re-ingest files to ensure they are indexed correctly."""
    logger.info("Starting re-ingestion process...")
    
    success_count = 0
    fail_count = 0
    
    for i, file_path in enumerate(files, 1):
        try:
            logger.info(f"[{i}/{len(files)}] Processing: {file_path.name}")
            
            # Force re-ingestion with explicit source type
            result = service.ingest_file(
                file_path=str(file_path),
                source_type="rescue_script",
                auto_commit=True,
                extra_metadata={"reindexed_by": "rescue_script"}
            )
            
            if result.success:
                success_count += 1
            else:
                logger.error(f"❌ Failed to ingest {file_path.name}: {result.error_message}")
                fail_count += 1
                
        except Exception as e:
            logger.error(f"❌ Exception processing {file_path.name}: {e}")
            fail_count += 1
            
    logger.info(f"Ingestion complete: {success_count} succeeded, {fail_count} failed")


def verify_system():
    """Run verification checks."""
    logger.info("Verifying RAG system status...")
    
    store = get_personal_library_store()
    
    # Check total documents using new list_all_documents method
    try:
        if hasattr(store, 'list_all_documents'):
            all_docs = store.list_all_documents()
            logger.info(f"✅ Total indexed documents: {len(all_docs)}")
            
            if len(all_docs) < 5:
                logger.warning("⚠️ Warning: Fewer than 5 documents indexed")
        else:
            # Fallback for older version check
            stats = store.get_stats()
            logger.info(f"Store stats: {stats}")
            
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")

    # Run test search
    test_query = "patient safety"
    logger.info(f"Running test search for: '{test_query}'")
    
    try:
        # Request more than 5 results to verify fix
        results = store.search(test_query, limit=10)
        logger.info(f"✅ Search returned {len(results)} results")
        
        for i, res in enumerate(results, 1):
            logger.info(f"  {i}. {res.filename} (Score: {res.score:.2f})")
            
        if len(results) > 5:
            logger.info("✅ SUCCESS: Retrieved > 5 results!")
        else:
            logger.warning(f"⚠️ Warning: Retrieved {len(results)} results (expected > 5 if enough matches)")
            
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")


def main():
    print("="*60)
    print("RAG SYSTEM RESCUE TOOL")
    print("="*60)
    
    check_environment()
    
    # Target directory
    target_dir = PROJECT_ROOT / "data" / "personal_library" / "indexed"
    files = scan_files(target_dir)
    
    if not files:
        logger.error("No files found to process. Exiting.")
        return

    # Initialize service
    service = KnowledgeIngestionService()
    
    # Ask for confirmation
    print(f"\nReady to re-ingest {len(files)} files.")
    print("This will update the vector index and ensure all metadata is correct.")
    # Auto-proceed in non-interactive mode or just proceed as this is a fix script
    
    reingest_files(service, files)
    verify_system()
    
    print("\n" + "="*60)
    print("Rescue complete.")
    print("="*60)


if __name__ == "__main__":
    main()
