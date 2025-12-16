#!/usr/bin/env python3
"""
Auto-Indexing Watch Script for Personal Library
Monitors folder for new files and automatically indexes them.

Updated: 2025-12-16 (Refactored to use KnowledgeIngestionService)

Usage:
    python scripts/watch_and_index.py

Stop: Press Ctrl+C
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Set

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use the unified ingestion service (R1 requirement)
from src.knowledge.ingestion_service import get_ingestion_service, KnowledgeIngestionService
from src.knowledge.vector_store import VectorStoreFactory
from src.knowledge.config import get_config

# Configuration
WATCH_FOLDER = project_root / "data" / "personal_library" / "to_synthesize"
INDEXED_FOLDER = project_root / "data" / "personal_library" / "indexed"
CHECK_INTERVAL = 5  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_folders():
    """Create watch and indexed folders if they don't exist."""
    WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
    INDEXED_FOLDER.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ Watch folder: {WATCH_FOLDER}")
    logger.info(f"✅ Indexed folder: {INDEXED_FOLDER}")


def get_files_in_folder(folder: Path, supported_extensions: Set[str]) -> Set[Path]:
    """Get all supported files in folder."""
    files = set()
    for ext in supported_extensions:
        files.update(folder.glob(f"*{ext}"))
    return files


def index_file(file_path: Path, service: KnowledgeIngestionService) -> bool:
    """Index a single file using KnowledgeIngestionService and move to indexed folder."""
    try:
        logger.info(f"Indexing: {file_path.name}")

        # Use the unified ingestion service
        result = service.ingest_file(
            file_path=str(file_path),
            store_type="personal",
            auto_commit=True,
        )

        if not result.success:
            logger.warning(f"No content extracted from {file_path.name}: {result.error_message}")
            return False

        # Move to indexed folder
        dest = INDEXED_FOLDER / file_path.name

        # Handle duplicate names
        counter = 1
        while dest.exists():
            name_parts = file_path.stem, counter, file_path.suffix
            dest = INDEXED_FOLDER / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1

        file_path.rename(dest)

        cache_info = ""
        if result.cache_hits > 0 or result.embedding_cache_hits > 0:
            cache_info = f" (cache: {result.cache_hits} chunks, {result.embedding_cache_hits} embeddings)"

        logger.info(f"Indexed {result.chunk_count} chunks from {file_path.name}{cache_info}")
        logger.info(f"Moved to: {dest}")
        return True

    except Exception as e:
        logger.error(f"Error indexing {file_path.name}: {e}")
        return False


def watch_and_index():
    """Main watch loop using KnowledgeIngestionService."""
    logger.info("=" * 80)
    logger.info("AUTO-INDEXING WATCH SCRIPT STARTED")
    logger.info("=" * 80)

    # Setup
    setup_folders()

    # Initialize service and config
    logger.info("Initializing ingestion service...")
    service = get_ingestion_service()
    config = get_config()
    supported_extensions = set(config.supported_extensions)

    logger.info(f"Checking for new files every {CHECK_INTERVAL} seconds")
    logger.info(f"Drop files here: {WATCH_FOLDER}")
    logger.info(f"Supported: {', '.join(supported_extensions)}")
    logger.info(f"Press Ctrl+C to stop\n")

    # Track already indexed files
    seen_files: Set[Path] = get_files_in_folder(WATCH_FOLDER, supported_extensions)

    if seen_files:
        logger.info(f"Found {len(seen_files)} existing files in watch folder")
        logger.info("Indexing existing files...")
        for file_path in seen_files:
            index_file(file_path, service)
        seen_files.clear()  # Clear after processing

    # Watch loop
    try:
        while True:
            current_files = get_files_in_folder(WATCH_FOLDER, supported_extensions)
            new_files = current_files - seen_files

            if new_files:
                logger.info(f"\nDetected {len(new_files)} new file(s)")
                for file_path in new_files:
                    if index_file(file_path, service):
                        seen_files.add(file_path)

                logger.info(f"\nWatching for more files... (Ctrl+C to stop)")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        logger.info("\n\nWatch script stopped by user")
        logger.info("=" * 80)

        # Show final stats
        store = VectorStoreFactory.get_store("personal")
        stats = store.get_stats()
        logger.info(f"Final Statistics:")
        logger.info(f"   Total chunks: {stats.get('chunk_count', 0)}")
        logger.info(f"   Collection: {stats.get('collection_name', 'unknown')}")
        logger.info("=" * 80)


if __name__ == "__main__":
    try:
        watch_and_index()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
