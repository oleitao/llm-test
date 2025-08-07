#!/usr/bin/env python3
"""
Test script to verify sentence-transformers is properly installed.
This script attempts to initialize and use a sentence-transformers model,
which is required by LanceDB.
"""

import sys

def test_sentence_transformers():
    print("Testing sentence-transformers installation...")
    
    try:
        import sentence_transformers
        print("✓ Successfully imported sentence_transformers module")
    except ImportError:
        print("✗ ERROR: sentence-transformers package not found!")
        print("  Please install it with: pip install sentence-transformers==2.2.2")
        return False

    try:
        from sentence_transformers import SentenceTransformer
        print("✓ Successfully imported SentenceTransformer class")
    except ImportError as e:
        print(f"✗ ERROR: Could not import SentenceTransformer class: {str(e)}")
        return False

    try:
        # Try importing the model registry from LanceDB
        from lancedb.embeddings import get_registry
        print("✓ Successfully imported LanceDB embedding registry")
        
        # Try getting the sentence-transformers embedding function
        registry = get_registry()
        embedding_fn = registry.get("sentence-transformers")
        print("✓ Successfully accessed sentence-transformers in registry")
        
        # Try creating an embedding model
        model = embedding_fn.create(name="all-mpnet-base-v2")
        print("✓ Successfully created embedding model")
        
        # Try generating embeddings
        test_text = "This is a test sentence."
        embeddings = model.generate_embeddings([test_text])
        print(f"✓ Successfully generated embeddings with shape: {len(embeddings[0])}")
        
        return True
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== SENTENCE-TRANSFORMERS TEST ===\n")
    success = test_sentence_transformers()
    
    if success:
        print("\n✅ All tests passed! sentence-transformers is properly installed.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
