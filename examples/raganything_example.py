#!/usr/bin/env python
"""
Example script demonstrating the integration of Ollama with RAGAnything

This example shows how to:
1. Process documents with RAGAnything using Ollama local models
2. Perform pure text queries using aquery() method
3. Perform multimodal queries with specific multimodal content using aquery_with_multimodal() method
4. Handle different types of multimodal content (tables, equations) in queries

Required Ollama models:
- mistral:latest (LLM model)
- llava:latest (Vision model)
- bge-m3:latest (Embedding model)
"""

import os
import sys
import argparse
import asyncio
import logging
import logging.config

from pathlib import Path
from typing import List, Dict, Optional


sys.path.append(str(Path(__file__).parent.parent))

from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc, logger, set_verbose_debug
from raganything import RAGAnything, RAGAnythingConfig

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "mistral:latest")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:latest")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3:latest")


async def ollama_llm_func(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: List[Dict] = None,
    **kwargs,
) -> str:
    """Ollama LLM function using mistral model."""
    return await openai_complete_if_cache(
        model=OLLAMA_LLM_MODEL,
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages or [],
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
        **kwargs,
    )


async def ollama_vision_func(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: List[Dict] = None,
    image_data: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
    **kwargs,
) -> str:
    """Ollama vision function using llava model."""
    # If messages format is provided (for multimodal VLM enhanced query), use it directly
    if messages:
        return await openai_complete_if_cache(
            model=OLLAMA_VISION_MODEL,
            prompt="",
            system_prompt=None,
            history_messages=[],
            messages=messages,
            base_url=OLLAMA_BASE_URL,
            api_key=OLLAMA_API_KEY,
            **kwargs,
        )
    # Traditional single image format
    elif image_data:
        return await openai_complete_if_cache(
            model=OLLAMA_VISION_MODEL,
            prompt="",
            system_prompt=None,
            history_messages=[],
            messages=[
                {"role": "system", "content": system_prompt} if system_prompt else None,
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                        },
                    ],
                }
                if image_data
                else {"role": "user", "content": prompt},
            ],
            base_url=OLLAMA_BASE_URL,
            api_key=OLLAMA_API_KEY,
            **kwargs,
        )
    # Pure text format - fallback to LLM
    else:
        return await ollama_llm_func(prompt, system_prompt, history_messages, **kwargs)


async def ollama_embedding_func(texts: List[str]) -> List[List[float]]:
    """Ollama embedding function using bge-m3 model."""
    embeddings = await openai_embed(
        texts=texts,
        model=OLLAMA_EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
    )
    return embeddings.tolist()


def configure_logging():
    """Configure logging for the application"""
    # Get log directory path from environment variable or use current directory
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "raganything_example.log"))

    print(f"\nRAGAnything example log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    # Get log file max size and backup count from environment variables
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))  # Default 10MB
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))  # Default 5 backups

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(levelname)s: %(message)s",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file_path,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "lightrag": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    # Set the logger level to INFO
    logger.setLevel(logging.INFO)
    # Enable verbose debug if needed
    set_verbose_debug(os.getenv("VERBOSE", "false").lower() == "true")


async def process_with_rag(
    file_path: str,
    output_dir: str,
    working_dir: str = None,
    parser: str = None,
):
    """
    Process document with RAGAnything using Ollama models

    Args:
        file_path: Path to the document
        output_dir: Output directory for RAG results
        working_dir: Working directory for RAG storage
        parser: Parser to use (mineru or docling)
    """
    try:
        # Create RAGAnything configuration
        config = RAGAnythingConfig(
            working_dir=working_dir or "./rag_storage",
            parser=parser,  # Parser selection: mineru or docling
            parse_method="auto",  # Parse method: auto, ocr, or txt
            enable_image_processing=True,
            enable_table_processing=True,
            enable_equation_processing=True,
        )

        # Define embedding function - using bge-m3 model (dimension: 1024)
        embedding_dim = int(os.getenv("EMBEDDING_DIM", "1024"))  # bge-m3 uses 1024 dimensions

        embedding_func = EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=8192,
            func=ollama_embedding_func,
        )

        # Initialize RAGAnything with Ollama models
        rag = RAGAnything(
            config=config,
            llm_model_func=ollama_llm_func,
            vision_model_func=ollama_vision_func,
            embedding_func=embedding_func,
        )

        # Process document
        await rag.process_document_complete(
            file_path=file_path, output_dir=output_dir, parse_method="auto"
        )

        # Example queries - demonstrating different query approaches
        logger.info("\nQuerying processed document:")

        # 1. Pure text queries using aquery()
        text_queries = [
            "What is the main content of the document?",
            "What are the key topics discussed?",
        ]

        for query in text_queries:
            logger.info(f"\n[Text Query]: {query}")
            result = await rag.aquery(query, mode="hybrid")
            logger.info(f"Answer: {result}")

        # 2. Multimodal query with specific multimodal content using aquery_with_multimodal()
        logger.info(
            "\n[Multimodal Query]: Analyzing performance data in context of document"
        )
        multimodal_result = await rag.aquery_with_multimodal(
            "Compare this performance data with any similar results mentioned in the document",
            multimodal_content=[
                {
                    "type": "table",
                    "table_data": """Method,Accuracy,Processing_Time
                                RAGAnything,95.2%,120ms
                                Traditional_RAG,87.3%,180ms
                                Baseline,82.1%,200ms""",
                    "table_caption": "Performance comparison results",
                }
            ],
            mode="hybrid",
        )
        logger.info(f"Answer: {multimodal_result}")

        # 3. Another multimodal query with equation content
        logger.info("\n[Multimodal Query]: Mathematical formula analysis")
        equation_result = await rag.aquery_with_multimodal(
            "Explain this formula and relate it to any mathematical concepts in the document",
            multimodal_content=[
                {
                    "type": "equation",
                    "latex": "F1 = 2 \\cdot \\frac{precision \\cdot recall}{precision + recall}",
                    "equation_caption": "F1-score calculation formula",
                }
            ],
            mode="hybrid",
        )
        logger.info(f"Answer: {equation_result}")

    except Exception as e:
        logger.error(f"Error processing with RAG: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())


def main():
    """Main function to run the example"""
    parser = argparse.ArgumentParser(description="RAGAnything with Ollama Example")
    parser.add_argument("file_path", help="Path to the document to process")
    parser.add_argument(
        "--working_dir", "-w", default="./rag_storage", help="Working directory path"
    )
    parser.add_argument(
        "--output", "-o", default="./output", help="Output directory path"
    )
    parser.add_argument(
        "--parser",
        default=os.getenv("PARSER", "mineru"),
        help="Parser to use: mineru or docling (default: mineru)",
    )

    args = parser.parse_args()

    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    # Process with RAG using Ollama
    asyncio.run(
        process_with_rag(
            args.file_path,
            args.output,
            args.working_dir,
            args.parser,
        )
    )


if __name__ == "__main__":
    # Configure logging first
    configure_logging()

    print("=" * 60)
    print("RAGAnything with Ollama Example")
    print("=" * 60)
    print("Processing document with multimodal RAG pipeline")
    print("Using Ollama local models:")
    print(f"  - LLM: {OLLAMA_LLM_MODEL}")
    print(f"  - Vision: {OLLAMA_VISION_MODEL}")
    print(f"  - Embedding: {OLLAMA_EMBEDDING_MODEL}")
    print(f"  - Base URL: {OLLAMA_BASE_URL}")
    print("=" * 60)

    main()