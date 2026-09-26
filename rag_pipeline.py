import os
from typing import List, Dict, Any
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

CHROMA_PATH = "chroma_db"
CORPUS_PATH = "corpus"

def get_embeddings_model():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def build_index():
    print("Building index...")
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    docs = []
    for filename in os.listdir(CORPUS_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(CORPUS_PATH, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            md_docs = markdown_splitter.split_text(content)
            for md_doc in md_docs:
                md_doc.metadata["source"] = filename
                md_doc.metadata["doc_id"] = filename.replace(".md", "")
                docs.append(md_doc)
                
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    )
    splits = text_splitter.split_documents(docs)
    
    embedding_function = get_embeddings_model()
    
    # Remove existing DB if it exists
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)
        
    db = Chroma.from_documents(splits, embedding_function, persist_directory=CHROMA_PATH)
    print(f"Index built with {len(splits)} chunks.")

def retrieve(query: str, k: int = 3) -> List[Dict[str, Any]]:
    embedding_function = get_embeddings_model()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    results = db.similarity_search_with_score(query, k=k)
    
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        })
        
    return formatted_results

if __name__ == "__main__":
    build_index()
