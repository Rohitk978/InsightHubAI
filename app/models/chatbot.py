import os
import json
import hashlib
import logging
import threading
import shutil

import torch
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    pipeline,
)
from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFacePipeline,
)
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

LLM_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
RERANKER_MODEL = "BAAI/bge-reranker-base"

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
DENSE_TOP_K = 8
BM25_TOP_K = 8
RERANK_TOP_K = 3
RRF_K = 60


class DocumentQA:

    def __init__(self):
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("RAG device: %s", self.device)

        # Keep embeddings on CPU to preserve VRAM for the LLM.
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": False},
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        self.llm, self.tokenizer = self._load_llm()

        # Keep the reranker on CPU because the GPU has only 4 GB VRAM.
        logger.info("Loading reranker: %s", RERANKER_MODEL)
        self.reranker = CrossEncoder(
            RERANKER_MODEL,
            device="cpu",
            max_length=512,
        )

        logger.info("DocumentQA initialized successfully.")

    def _load_llm(self):
        logger.info("Loading local LLM: %s", LLM_MODEL)

        tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)

        if self.device == "cuda":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )

            model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL,
                quantization_config=quantization_config,
                torch_dtype=torch.float16,
                device_map={"": 0},
                low_cpu_mem_usage=True,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
            )

        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=128,
            do_sample=False,
            return_full_text=False,
            pad_token_id=tokenizer.eos_token_id,
        )

        logger.info("LLM loaded successfully.")
        return HuggingFacePipeline(pipeline=generator), tokenizer

    @staticmethod
    def make_hash(content):
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def _paths(self, document_hash):
        index_dir = os.path.join(VECTOR_DB_DIR, document_hash)

        return {
            "directory": index_dir,
            "faiss": os.path.join(index_dir, "index.faiss"),
            "pickle": os.path.join(index_dir, "index.pkl"),
            "chunks": os.path.join(index_dir, "chunks.json"),
            "metadata": os.path.join(index_dir, "metadata.json"),
        }

    def index_exists(self, document_hash):
        paths = self._paths(document_hash)

        if not all(
            os.path.isfile(paths[key])
            for key in ("faiss", "pickle", "chunks", "metadata")
        ):
            return False

        try:
            with open(paths["metadata"], "r", encoding="utf-8") as file:
                metadata = json.load(file)

            return (
                metadata.get("embedding_model") == EMBEDDING_MODEL
                and metadata.get("chunk_size") == CHUNK_SIZE
                and metadata.get("chunk_overlap") == CHUNK_OVERLAP
                and metadata.get("schema_version") == 1
            )
        except (OSError, ValueError, TypeError):
            return False

    def get_or_create_vectorstore(self, document_hash, document=None):
        paths = self._paths(document_hash)

        if self.index_exists(document_hash):
            logger.info("Reusing saved FAISS index: %s", document_hash)

            vectorstore = FAISS.load_local(
                paths["directory"],
                self.embeddings,
                allow_dangerous_deserialization=True,
            )

            with open(paths["chunks"], "r", encoding="utf-8") as file:
                chunks = json.load(file)

            documents = [
                Document(page_content=text, metadata={"chunk_id": i})
                for i, text in enumerate(chunks)
            ]

            return vectorstore, documents

        if not document or not document.strip():
            raise ValueError(
                "Document text is required to build a new index."
            )

        logger.info("Creating a new index: %s", document_hash)

        chunks = self.splitter.split_text(document)

        if not chunks:
            raise ValueError("No usable text chunks were generated.")

        documents = [
            Document(page_content=text, metadata={"chunk_id": i})
            for i, text in enumerate(chunks)
        ]

        vectorstore = FAISS.from_documents(
            documents,
            self.embeddings,
        )

        temp_dir = paths["directory"] + ".tmp"
        shutil.rmtree(temp_dir, ignore_errors=True)
        os.makedirs(temp_dir, exist_ok=True)

        try:
            vectorstore.save_local(temp_dir)

            with open(
                os.path.join(temp_dir, "chunks.json"),
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(chunks, file, ensure_ascii=False)

            metadata = {
                "schema_version": 1,
                "embedding_model": EMBEDDING_MODEL,
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "document_hash": document_hash,
                "chunk_count": len(chunks),
            }

            with open(
                os.path.join(temp_dir, "metadata.json"),
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(metadata, file, indent=2)

            if os.path.exists(paths["directory"]):
                shutil.rmtree(paths["directory"])

            os.replace(temp_dir, paths["directory"])

        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

        logger.info("Saved %s chunks to %s", len(chunks), paths["directory"])

        return vectorstore, documents

    def prepare_document(self, document_hash, document=None):
        """Build or reuse the index for a document without answering.

        Used when loading/switching a source so the embeddings are
        created (or an existing persistent index is reused) up front.
        """
        self.get_or_create_vectorstore(
            document_hash=document_hash,
            document=document,
        )

    @staticmethod
    def _tokenize(text):
        return text.lower().split()

    def _hybrid_retrieve(self, question, vectorstore, documents):
        # Dense semantic retrieval through FAISS.
        dense_docs = vectorstore.similarity_search(
            question,
            k=min(DENSE_TOP_K, len(documents)),
        )

        # Sparse keyword retrieval through BM25.
        tokenized_chunks = [
            self._tokenize(doc.page_content)
            for doc in documents
        ]

        bm25 = BM25Okapi(tokenized_chunks)
        tokenized_question = self._tokenize(question)

        bm25_docs = bm25.get_top_n(
            tokenized_question,
            documents,
            n=min(BM25_TOP_K, len(documents)),
        )

        # Reciprocal Rank Fusion combines rankings, not raw scores.
        fused_scores = {}
        document_by_text = {}

        for ranked_docs in (dense_docs, bm25_docs):
            seen_in_list = set()

            for rank, doc in enumerate(ranked_docs, start=1):
                text = doc.page_content

                if text in seen_in_list:
                    continue

                seen_in_list.add(text)
                document_by_text[text] = doc

                fused_scores[text] = (
                    fused_scores.get(text, 0.0)
                    + 1.0 / (RRF_K + rank)
                )

        ranked_texts = sorted(
            fused_scores,
            key=fused_scores.get,
            reverse=True,
        )

        candidates = [
            document_by_text[text]
            for text in ranked_texts[:min(10, len(ranked_texts))]
        ]

        return candidates

    def _rerank(self, question, candidates):
        if not candidates:
            return []

        pairs = [
            (question, doc.page_content)
            for doc in candidates
        ]

        scores = self.reranker.predict(
            pairs,
            show_progress_bar=False,
        )

        ranked = sorted(
            zip(candidates, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            doc for doc, _ in ranked[:RERANK_TOP_K]
        ]

    def answer_query(self, document_hash, question, document=None):
        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        try:
            vectorstore, documents = self.get_or_create_vectorstore(
                document_hash=document_hash,
                document=document,
            )

            candidates = self._hybrid_retrieve(
                question,
                vectorstore,
                documents,
            )

            source_docs = self._rerank(question, candidates)

            if not source_docs:
                return {
                    "result": (
                        "I could not find relevant information "
                        "in the provided document."
                    ),
                    "source_documents": [],
                }

            context = "\n\n".join(
                doc.page_content for doc in source_docs
            )

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a document question-answering assistant. "
                        "Answer using only the supplied context. "
                        "If the answer is absent, say that the information "
                        "is not available in the document. "
                        "Do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Context:\n{context}\n\n"
                        f"Question: {question}"
                    ),
                },
            ]

            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

            with torch.inference_mode():
                answer = self.llm.invoke(prompt)

            return {
                "result": answer.strip(),
                "source_documents": source_docs,
            }

        except Exception:
            logger.exception("Question-answering pipeline failed.")
            raise


_document_qa = None
_document_qa_lock = threading.Lock()


def get_document_qa():
    global _document_qa

    if _document_qa is None:
        with _document_qa_lock:
            if _document_qa is None:
                _document_qa = DocumentQA()

    return _document_qa
