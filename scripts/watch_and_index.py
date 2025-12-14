#!/usr/bin/env python3
"""
Auto-Indexing Watch Script for Personal Library
Monitors folder for new files and automatically indexes them

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

from src.knowledge.vector_store import PersonalLibraryVectorStore
from src.knowledge.document_processor import DocumentProcessor

# Configuration
WATCH_FOLDER = project_root / "data" / "personal_library" / "to_synthesize"
INDEXED_FOLDER = project_root / "data" / "personal_library" / "indexed"
CHECK_INTERVAL = 5  # seconds
SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt", ".docx", ".pptx"}

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


def get_files_in_folder(folder: Path) -> Set[Path]:
    """Get all supported files in folder."""
    files = set()
    for ext in SUPPORTED_EXTENSIONS:
        files.update(folder.glob(f"*{ext}"))
    return files


def index_file(file_path: Path, store: PersonalLibraryVectorStore, processor: DocumentProcessor):
    """Index a single file and move it to indexed folder."""
    try:
        logger.info(f"📄 Indexing: {file_path.name}")
        
        # Process document
        chunks = processor.process_file(str(file_path))
        
        if not chunks:
            logger.warning(f"⚠️  No content extracted from {file_path.name}")
            return False
        
        # Add to vector store
        store.add_documents(chunks)
        
        # Move to indexed folder
        dest = INDEXED_FOLDER / file_path.name
        
        # Handle duplicate names
        counter = 1
        while dest.exists():
            name_parts = file_path.stem, counter, file_path.suffix
            dest = INDEXED_FOLDER / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1
        
        file_path.rename(dest)
        
        logger.info(f"✅ Indexed {len(chunks)} chunks from {file_path.name}")
        logger.info(f"📁 Moved to: {dest}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error indexing {file_path.name}: {e}")
        return False


def watch_and_index():
    """Main watch loop."""
    logger.info("=" * 80)
    logger.info("🔍 AUTO-INDEXING WATCH SCRIPT STARTED")
    logger.info("=" * 80)
    
    # Setup
    setup_folders()
    
    # Initialize store and processor
    logger.info("Initializing vector store and document processor...")
    store = PersonalLibraryVectorStore()
    processor = DocumentProcessor()
    
    logger.info(f"\n⏰ Checking for new files every {CHECK_INTERVAL} seconds")
    logger.info(f"📂 Drop files here: {WATCH_FOLDER}")
    logger.info(f"🛑 Press Ctrl+C to stop\n")
    
    # Track already indexed files
    seen_files: Set[Path] = get_files_in_folder(WATCH_FOLDER)
    
    if seen_files:
        logger.info(f"Found {len(seen_files)} existing files in watch folder")
        logger.info("Indexing existing files...")
        for file_path in seen_files:
            index_file(file_path, store, processor)
        seen_files.clear()  # Clear after processing
    
    # Watch loop
    try:
        while True:
            current_files = get_files_in_folder(WATCH_FOLDER)
            new_files = current_files - seen_files
            
            if new_files:
                logger.info(f"\n🆕 Detected {len(new_files)} new file(s)")
                for file_path in new_files:
                    if index_file(file_path, store, processor):
                        seen_files.add(file_path)
                
                logger.info(f"\n⏰ Watching for more files... (Ctrl+C to stop)")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Watch script stopped by user")
        logger.info("=" * 80)
        
        # Show final stats
        stats = store.get_stats()
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   Total documents: {stats.get('chunk_count', 0)}")
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
