#!/usr/bin/env python3
"""
Document Ingestion CLI for Personal Knowledge Library
Command-line tool for managing personal document library.

Created: 2025-12-13
Phase: B5

Usage:
    python scripts/ingest_documents.py add /path/to/file.pdf
    python scripts/ingest_documents.py add-folder /path/to/docs/
    python scripts/ingest_documents.py list
    python scripts/ingest_documents.py remove <doc_id>
    python scripts/ingest_documents.py stats
    python scripts/ingest_documents.py search "query text"
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.knowledge.document_ingester import DocumentIngester, ChunkRecord
from src.knowledge.vector_store import (
    PersonalLibraryVectorStore,
    get_personal_library_store,
    COLLECTION_PERSONAL,
)

# Default paths
DEFAULT_DB_PATH = str(PROJECT_ROOT / "data" / "chroma_db")
DEFAULT_LIBRARY_PATH = str(PROJECT_ROOT / "data" / "personal_library")


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"  ✅ {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"  ❌ {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"  ⚠️  {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"  ℹ️  {message}")


def get_store(db_path: str = DEFAULT_DB_PATH) -> PersonalLibraryVectorStore:
    """Get or create the vector store."""
    return get_personal_library_store(
        collection_name=COLLECTION_PERSONAL,
        db_path=db_path
    )


def cmd_add(args: argparse.Namespace) -> int:
    """Add a single file to the library."""
    file_path = Path(args.file)

    print_header("Add Document to Personal Library")

    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return 1

    if not file_path.is_file():
        print_error(f"Not a file: {file_path}")
        return 1

    print_info(f"Processing: {file_path.name}")

    try:
        # Initialize ingester
        ingester = DocumentIngester(
            chunk_size=args.chunk_size,
            overlap=args.overlap
        )

        # Check if format is supported
        if file_path.suffix.lower() not in ingester.SUPPORTED_FORMATS:
            print_error(f"Unsupported format: {file_path.suffix}")
            print_info(f"Supported: {', '.join(ingester.SUPPORTED_FORMATS.keys())}")
            return 1

        # Ingest file
        chunks = ingester.ingest_file(str(file_path))

        if not chunks:
            print_error("No content extracted from file")
            return 1

        print_info(f"Extracted {len(chunks)} chunks")

        # Store in vector database
        store = get_store(args.db_path)
        count = store.add_chunks(chunks)

        print_success(f"Added {count} chunks to library")
        print_info(f"Document ID: {chunks[0].doc_id}")

        return 0

    except Exception as e:
        print_error(f"Failed to add document: {e}")
        return 1


def cmd_add_folder(args: argparse.Namespace) -> int:
    """Add all documents from a folder."""
    folder_path = Path(args.folder)

    print_header("Add Folder to Personal Library")

    if not folder_path.exists():
        print_error(f"Folder not found: {folder_path}")
        return 1

    if not folder_path.is_dir():
        print_error(f"Not a directory: {folder_path}")
        return 1

    print_info(f"Scanning: {folder_path}")
    print_info(f"Recursive: {args.recursive}")

    try:
        # Initialize ingester
        ingester = DocumentIngester(
            chunk_size=args.chunk_size,
            overlap=args.overlap
        )

        # Get supported files
        if args.recursive:
            files = list(folder_path.rglob("*"))
        else:
            files = list(folder_path.glob("*"))

        supported_files = [
            f for f in files
            if f.is_file() and f.suffix.lower() in ingester.SUPPORTED_FORMATS
        ]

        if not supported_files:
            print_warning("No supported files found")
            print_info(f"Supported formats: {', '.join(ingester.SUPPORTED_FORMATS.keys())}")
            return 0

        print_info(f"Found {len(supported_files)} supported files")
        print()

        # Process files with progress
        store = get_store(args.db_path)
        success_count = 0
        fail_count = 0
        total_chunks = 0

        for i, file_path in enumerate(supported_files, 1):
            # Progress indicator
            progress = f"[{i}/{len(supported_files)}]"
            print(f"  {progress} Processing: {file_path.name}...", end=" ", flush=True)

            try:
                chunks = ingester.ingest_file(str(file_path))
                if chunks:
                    store.add_chunks(chunks)
                    total_chunks += len(chunks)
                    success_count += 1
                    print(f"✓ ({len(chunks)} chunks)")
                else:
                    fail_count += 1
                    print("✗ (no content)")
            except Exception as e:
                fail_count += 1
                print(f"✗ ({str(e)[:30]}...)")

        print()
        print_header("Summary")
        print_success(f"Successfully processed: {success_count} files")
        if fail_count > 0:
            print_warning(f"Failed: {fail_count} files")
        print_info(f"Total chunks added: {total_chunks}")

        return 0 if fail_count == 0 else 1

    except Exception as e:
        print_error(f"Failed to process folder: {e}")
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List all indexed documents."""
    print_header("Indexed Documents")

    try:
        store = get_store(args.db_path)
        docs = store.list_documents()

        if not docs:
            print_info("No documents indexed yet")
            print_info("Use 'add' or 'add-folder' to add documents")
            return 0

        print(f"  {'Document ID':<20} {'Filename':<30} {'Chunks':<8} {'Ingested':<20}")
        print(f"  {'-'*20} {'-'*30} {'-'*8} {'-'*20}")

        for doc in docs:
            doc_id = doc.get("doc_id", "")[:18]
            filename = doc.get("filename", "unknown")[:28]
            chunks = doc.get("chunk_count", 0)
            ingested = doc.get("ingested_at", "")[:19]

            print(f"  {doc_id:<20} {filename:<30} {chunks:<8} {ingested:<20}")

        print()
        print_info(f"Total: {len(docs)} documents")

        return 0

    except Exception as e:
        print_error(f"Failed to list documents: {e}")
        return 1


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a document from the library."""
    doc_id = args.doc_id

    print_header("Remove Document")

    try:
        store = get_store(args.db_path)

        print_info(f"Removing document: {doc_id}")

        result = store.delete_document(doc_id)

        if result:
            print_success("Document removed successfully")
            return 0
        else:
            print_warning("Document not found or already removed")
            return 1

    except Exception as e:
        print_error(f"Failed to remove document: {e}")
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Show library statistics."""
    print_header("Library Statistics")

    try:
        store = get_store(args.db_path)
        stats = store.get_stats()
        docs = store.list_documents()

        print(f"  Collection:     {stats.get('collection_name', 'unknown')}")
        print(f"  Database Path:  {stats.get('db_path', 'unknown')}")
        print(f"  Status:         {'Active' if stats.get('exists') else 'Not initialized'}")
        print()
        print(f"  Total Documents: {len(docs)}")
        print(f"  Total Chunks:    {stats.get('chunk_count', 0)}")
        print(f"  Embedder:        {stats.get('embedder', 'unknown')}")

        if docs:
            # Calculate some additional stats
            total_chunks = sum(d.get("chunk_count", 0) for d in docs)
            avg_chunks = total_chunks / len(docs) if docs else 0

            print()
            print(f"  Avg Chunks/Doc:  {avg_chunks:.1f}")

            # File type breakdown
            extensions = {}
            for doc in docs:
                filename = doc.get("filename", "")
                ext = Path(filename).suffix.lower() if filename else "unknown"
                extensions[ext] = extensions.get(ext, 0) + 1

            if extensions:
                print()
                print("  File Types:")
                for ext, count in sorted(extensions.items(), key=lambda x: -x[1]):
                    print(f"    {ext or 'unknown'}: {count}")

        return 0

    except Exception as e:
        print_error(f"Failed to get stats: {e}")
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Search the library (for testing)."""
    query = args.query

    print_header(f"Search: {query}")

    try:
        store = get_store(args.db_path)
        results = store.search(query, limit=args.limit)

        if not results:
            print_info("No results found")
            return 0

        print(f"  Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result.filename}]")
            if result.page_num:
                print(f"     Page: {result.page_num}")
            print(f"     Score: {result.score:.3f}")
            text_preview = result.text[:150].replace('\n', ' ')
            print(f"     \"{text_preview}...\"")
            print()

        return 0

    except Exception as e:
        print_error(f"Search failed: {e}")
        return 1


def cmd_clear(args: argparse.Namespace) -> int:
    """Clear all documents from the library."""
    print_header("Clear Library")

    if not args.force:
        print_warning("This will delete ALL documents from the library!")
        response = input("  Are you sure? (yes/no): ")
        if response.lower() != "yes":
            print_info("Cancelled")
            return 0

    try:
        store = get_store(args.db_path)
        store.clear()
        print_success("Library cleared successfully")
        return 0

    except Exception as e:
        print_error(f"Failed to clear library: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Personal Knowledge Library - Document Ingestion CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add research_paper.pdf
  %(prog)s add-folder ./my_documents/ --recursive
  %(prog)s list
  %(prog)s stats
  %(prog)s search "fall prevention protocols"
  %(prog)s remove abc123def456
        """
    )

    # Global options
    parser.add_argument(
        "--db-path",
        default=DEFAULT_DB_PATH,
        help=f"Path to ChromaDB storage (default: {DEFAULT_DB_PATH})"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a single document")
    add_parser.add_argument("file", help="Path to the document file")
    add_parser.add_argument(
        "--chunk-size", type=int, default=2000,
        help="Target chunk size in characters (default: 2000)"
    )
    add_parser.add_argument(
        "--overlap", type=int, default=200,
        help="Overlap between chunks (default: 200)"
    )

    # Add-folder command
    folder_parser = subparsers.add_parser("add-folder", help="Add all documents from a folder")
    folder_parser.add_argument("folder", help="Path to the folder")
    folder_parser.add_argument(
        "--recursive", "-r", action="store_true",
        help="Process subdirectories recursively"
    )
    folder_parser.add_argument(
        "--chunk-size", type=int, default=2000,
        help="Target chunk size in characters (default: 2000)"
    )
    folder_parser.add_argument(
        "--overlap", type=int, default=200,
        help="Overlap between chunks (default: 200)"
    )

    # List command
    subparsers.add_parser("list", help="List all indexed documents")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a document by ID")
    remove_parser.add_argument("doc_id", help="Document ID to remove")

    # Stats command
    subparsers.add_parser("stats", help="Show library statistics")

    # Search command (for testing)
    search_parser = subparsers.add_parser("search", help="Search the library")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--limit", "-n", type=int, default=5,
        help="Maximum results (default: 5)"
    )

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear all documents")
    clear_parser.add_argument(
        "--force", "-f", action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to command handler
    commands = {
        "add": cmd_add,
        "add-folder": cmd_add_folder,
        "list": cmd_list,
        "remove": cmd_remove,
        "stats": cmd_stats,
        "search": cmd_search,
        "clear": cmd_clear,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print_error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
