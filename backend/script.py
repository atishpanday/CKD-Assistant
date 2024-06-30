import os
import re
import pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
import asyncio

from utils.pinecone_client import get_pinecone_client
from utils.embeddings import get_embeddings

# Initialize Pinecone client
pc = get_pinecone_client()
index = pc.Index(os.getenv("PINECONE_INDEX"))


def process_pdf(file_path):
    # Create a loader
    loader = PyPDFLoader(file_path)
    # Load your data
    data = loader.load()
    # Split your data up into smaller documents with Chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = text_splitter.split_documents(data)
    return documents


def embed_docs(docs):
    cohereEmbedding = get_embeddings()
    PineconeVectorStore.from_documents(
        docs, embedding=cohereEmbedding, index_name=os.getenv("PINECONE_INDEX")
    )


# Main function to run the process
async def main():
    file_path = "assets/HFHS_CKD_V6.pdf"  # Replace with your actual file path
    docs = process_pdf(file_path)
    # Upsert the embeddings to Pinecone
    embed_docs(docs)


# Run the main function
asyncio.run(main())
