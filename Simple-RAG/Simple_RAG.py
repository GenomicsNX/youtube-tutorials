!pip install -qU chromadb
!pip install -qU openai
!pip install -qU pypdf2
!pip install -qU python-docx
!pip install -qU sentence-transformers

import docx
import PyPDF2
import os

def read_text_file(file_path: str):
    """Read content from a text file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_pdf_file(file_path: str):
    """Read Content From a PDF File"""
    text=""
    with open(file_path, "rb") as file:
        pdf_reader=PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def read_docx_file(file_path: str):
    """Read content from a Word document"""
    doc = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def read_document(file_path: str):
    """Read Document Content Based on File Extension"""
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    if file_extension == ".txt":
        return read_text_file(file_path)
    elif file_extension == ".pdf":
        return read_pdf_file(file_path)
    elif file_extension == ".docx":
        return read_docx_file(file_path)
    else:
        raise ValueError(f"Unsupported File Format: {file_extension}")

!gdown "https://drive.google.com/uc?id=1v4_2O15UPjaUEZO-7oijqSWFDnQiEG6t&confirm=t"

file_path = "/content/yolov7_paper.pdf"

text = read_document(file_path)

print("\n======Extracted PDF Content=======\n")
print(text[:500])

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100):
    """Split text into overlapping chunks (very simple version)."""
    text = text.replace("\n", " ").strip()
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - chunk_overlap

    return chunks

sample = "This is a very long paragraph of text that you want to split into smaller chunks for embedding or storage."
chunks = split_text(sample, chunk_size=10, chunk_overlap=2)
print(chunks)

chunks = split_text(text, chunk_size=500, chunk_overlap=50)

print("Chunk-01", chunks[0])
print("Chunk-02", chunks[1])
print("Number of Chunks", len(chunks))

import chromadb

from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="chroma_db")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="documents_collection",
    embedding_function=sentence_transformer_ef
)

def process_document(file_path: str):
    """Process a single document and prepare it for ChromaDB"""
    try:
        content = read_document(file_path)

        chunks = split_text(content)

        file_name = os.path.basename(file_path)
        metadatas = [{"source": file_name, "chunk": i} for i in range(len(chunks))]
        ids = [f"{file_name}_chunk_{i}" for i in range(len(chunks))]

        return ids, chunks, metadatas
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return [], [], []

ids, chunks, metadatas = process_document(file_path)

print("id[0] -> ", ids[0])
print("metadatas[0] -> ", metadatas[0])
print("chunks[0] -> ", chunks[0])

len(chunks)

collection.add(documents=chunks, metadatas=metadatas, ids=ids)

def semantic_search(collection, query: str, n_results: int = 2):
    """Perform a minimal semantic search."""
    return collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas"]
    )

def get_context_with_sources(results):
    """This takes the search results from the previous function and makes them easy to use, a clean paragraph of text (context), a list of where it came from (sources)"""
    if not results or not results.get("documents") or not results["documents"][0]:
        return "", []

    context = "\n\n".join(results["documents"][0])

    seen = set()
    sources = []
    for meta in results["metadatas"][0]:
        label = f"{meta.get('source','?')} (chunk {meta.get('chunk','?')})"
        if label not in seen:
            seen.add(label)
            sources.append(label)

    return context, sources

def ask(collection, query: str, n_results: int = 2):
    """One-call helper: search, build context, and print sources."""

    results = semantic_search(collection, query, n_results=n_results)

    context, sources = get_context_with_sources(results)

    print("\n=== CONTEXT ===\n")
    print(context or "[No matching text found]")

    print("\n=== SOURCES ===")
    if sources:
        for i, s in enumerate(sources, 1):
            print(f"{i}. {s}")
    else:
        print("[No sources]")

    return context, sources

query = "What is YOLOv7"
context, sources = ask(collection, query, n_results=5)

OPEN_ROUTER_API_KEY = "***"
OPEN_ROUTER_MODEL_NAME = "openai/gpt-oss-120b:free"

from openai import OpenAI

client = OpenAI(
  base_url = "https://openrouter.ai/api/v1",
  api_key = OPEN_ROUTER_API_KEY,
)

SYSTEM_PROMPT = (
    "You are a helpful assistant for retrieval-augmented generation (RAG).\n"
    "Answer ONLY using the provided context. "
    "If the answer is not found in the context, say: "
    "'I don't know based on the provided documents.'"
)

def build_messages(context: str, question: str):
    """Create messages for OpenAI API."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"}
    ]

def rag_answer(collection, query: str, n_results: int = 4, model: str = OPEN_ROUTER_MODEL_NAME):
    """Run semantic search + OpenAI generation, and print results."""
    results = semantic_search(collection, query, n_results)
    context, sources = get_context_with_sources(results)

    if not context.strip():
        print("⚠️ No relevant context found.")
        return "", []

    messages = build_messages(context, query)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=512
    )

    answer = response.choices[0].message.content.strip()

    print("\n=== ANSWER ===\n")
    print(answer or "[No answer generated]")

    print("\n=== SOURCES ===")
    if sources:
        for i, s in enumerate(sources, 1):
            print(f"{i}. {s}")
    else:
        print("[No sources found]")

    return answer, sources

query = "YOLOv7 outperforms which models"
rag_answer(collection, query, n_results=2)

query = "Provide me an introduction to YOLOv7"
rag_answer(collection, query, n_results=2)

query = "What are extended efficient layer aggregation networks"
rag_answer(collection, query, n_results=5)