<<<<<<< HEAD
# import os
# import numpy as np
# import faiss
# import pdfplumber
# import logging
# import torch
# import traceback
# from transformers import (
#     AutoTokenizer,
#     AutoModelForCausalLM,
#     BitsAndBytesConfig,
#     pipeline
# )



# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_huggingface import HuggingFacePipeline
# from langchain.prompts import PromptTemplate
# from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# # Converts models output into plain string.
# from langchain_core.output_parsers import StrOutputParser

# # configure logging system.
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
# logging.getLogger("langchain_community.vectorstores.faiss").setLevel(logging.WARNING)

# class DocumentQA:

#     def __init__(self, document, is_pdf=False):
#         """Initialize the QA system with a document (text or PDF content)."""
        
#         # Checking if GPU is available or not.
#         self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
#         logger.info(f"Using device: {self.device}")
        
#         # Set custom cache directory
#         cache_dir = "D://huggingface_cache"
#         os.makedirs(cache_dir, exist_ok=True)

#         # Using pre-trained sentence transformer which takes the text data and convert it into dense vector using GPU device if available.
#         model_name = "BAAI/bge-small-en-v1.5"
#         model_kwargs = {'device': self.device}
#         encode_kwargs = {'normalize_embeddings': False}

#         # Initialize Hugging Face Embeddings with error handling
=======
# from flask import current_app
# import numpy as np
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.llms import HuggingFacePipeline
# from langchain.chains import RetrievalQA
# from langchain_core.prompts import PromptTemplate
# import faiss
# import logging
# import pdfplumber
# from PIL import Image
# import pytesseract
# import os
# import torch
# from transformers import pipeline
# import traceback

# # Setup logging
# logger = logging.getLogger(__name__)
# logging.getLogger('langchain_community.vectorstores.faiss').setLevel(logging.WARNING)

# class CustomHuggingFacePipeline(HuggingFacePipeline):
#     """Custom pipeline to handle question-answering input formatting."""
#     def _call(self, prompt, **kwargs):
#         try:
#             logger.debug(f"Received prompt: {prompt}")
#             if isinstance(prompt, dict) and "question" in prompt and "context" in prompt:
#                 result = self.pipeline({"question": prompt["question"], "context": prompt["context"]}, **kwargs)
#             else:
#                 # Parse string prompt with clear delimiters
#                 if "Context:" not in prompt or "Question:" not in prompt:
#                     raise ValueError("Invalid prompt format: 'Context:' or 'Question:' not found")
#                 parts = prompt.split("Question:", 1)
#                 if len(parts) != 2:
#                     raise ValueError("Invalid prompt format: cannot split on 'Question:'")
#                 context = parts[0].replace("Context:", "").strip()
#                 question = parts[1].split("Answer:", 1)[0].strip()
#                 result = self.pipeline({"question": question, "context": context}, **kwargs)
#             return result["answer"]
#         except Exception as e:
#             logger.error(f"Pipeline error: {str(e)}\n{traceback.format_exc()}")
#             raise ValueError(f"Pipeline processing failed: {str(e)}")

# class DocumentQA:
#     """Class for question-answering on documents using embeddings and QA pipeline."""
#     def __init__(self, document, is_file=False, chunk_size=500, chunk_overlap=50):
#         # Document processing
#         if is_file:
#             if not os.path.exists(document):
#                 logger.error(f"PDF file not found: {document}")
#                 raise ValueError("PDF file not found.")
#             self.text = self._extract_text_from_pdf(document)
#         else:
#             if not document or not isinstance(document, str) or not document.strip():
#                 logger.error("Invalid or empty text document provided")
#                 raise ValueError("Text document is empty or invalid.")
#             self.text = document

#         if not self.text.strip():
#             logger.error("No text extracted from input")
#             raise ValueError("No text could be extracted from the input.")

#         # Text splitting
#         self.text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

#         # Embeddings initialization
#         model_name = "sentence-transformers/all-mpnet-base-v2"
#         model_kwargs = {
#             'device': 'cuda' if current_app.config.get('CUDA_AVAILABLE', False) and torch.cuda.is_available() else 'cpu'
#         }
#         encode_kwargs = {'normalize_embeddings': False}
>>>>>>> origin/main
#         try:
#             self.hf_embeddings = HuggingFaceEmbeddings(
#                 model_name=model_name,
#                 model_kwargs=model_kwargs,
#                 encode_kwargs=encode_kwargs
#             )
<<<<<<< HEAD

#         except Exception as e:
#             logger.error(f"Embedding initialization failed: {str(e)}")
#             raise RuntimeError(f"Embedding initialization failed: {str(e)}")

#         # Process document
#         try:
#             # checking if pdf is available or not.
#             if is_pdf:
#                 # using pdfplumber to iterate through pages of pdf and extract text from pages and checking if text is availabel and put the extracted text into text string vaiable.
#                 with pdfplumber.open(document) as pdf:
#                     text = ""
#                     for page in pdf.pages:
#                         page_text = page.extract_text()
#                         if page_text:
#                             text += page_text + "\n"
#             else:
#                 text = document
            
#             # no text is extracted from pdf.
#             if not text.strip():
#                 raise ValueError("No text could be extracted from the document.")
#         except Exception as e:
#             logger.error(f"Error processing document: {str(e)}")
#             raise RuntimeError(f"Error processing document: {str(e)}")

#         # Split extracted text into chunks so model can fit and process it effeciently.
#         try:
#             text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#             self.text_split = text_splitter.split_text(text)
#             if not self.text_split:
#                 raise ValueError("Text splitting failed: no documents generated.")
#         except Exception as e:
#             logger.error(f"Text splitter initialization failed: {str(e)}")
#             raise ValueError(f"Text splitter initialization failed: {str(e)}")

#         # Create FAISS vectorstore
#         try:
#             sample_embedding = np.array(self.hf_embeddings.embed_query("sample text"))
#             dimension = sample_embedding.shape[0]
#             index = faiss.IndexFlatL2(dimension)
#             self.vectorstore = FAISS(
#                 embedding_function=self.hf_embeddings.embed_query,
=======
#         except Exception as e:
#             logger.error(f"Embedding initialization failed: {str(e)}\n{traceback.format_exc()}")
#             raise ValueError(f"Embedding initialization failed: {str(e)}")

#         # FAISS index initialization
#         sample_embedding = np.array(self.hf_embeddings.embed_query("sample text"))
#         dimension = sample_embedding.shape[0]
#         if current_app.config.get('CUDA_AVAILABLE', False) and torch.cuda.is_available():
#             try:
#                 res = faiss.StandardGpuResources()
#                 index = faiss.GpuIndexFlatL2(res, dimension)
#                 logger.info("Initialized FAISS index with GPU support")
#             except Exception as e:
#                 logger.warning(f"GPU FAISS failed: {str(e)}\n{traceback.format_exc()}")
#                 index = faiss.IndexFlatL2(dimension)
#                 logger.info("Initialized FAISS index with CPU support")
#         else:
#             index = faiss.IndexFlatL2(dimension)
#             logger.info("Initialized FAISS index with CPU support")

#         # Vector store setup
#         try:
#             self.vectorstore = FAISS(
#                 embedding_function=self.hf_embeddings,
>>>>>>> origin/main
#                 index=index,
#                 docstore=InMemoryDocstore(),
#                 index_to_docstore_id={}
#             )
<<<<<<< HEAD
#             self.vectorstore.add_texts(texts=self.text_split)
#         except Exception as e:
#             logger.error(f"Vector store setup failed: {str(e)}")
#             raise RuntimeError(f"Vector store setup failed: {str(e)}")
 
#         # Initialize LLM via Hugging Face Endpoint
#         token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
#         try:
#             # intializing the LLM model from hugging face hub using token and model repo id and provider so we can use the model through API without running it locally.
#             # self.llm = HuggingFaceEndpoint(
#             #     repo_id="Qwen/Qwen2.5-3B-Instruct",
#             #     huggingfacehub_api_token=token,
#             #     temperature=0.6,
#             #     provider="hf-inference"
#             # )
#             llm_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
#             quantization_config = BitsAndBytesConfig(
#                 load_in_4bit=True,
#                 bnb_4bit_quant_type="nf4",
#                 bnb_4bit_compute_dtype=torch.float16,
#                 bnb_4bit_use_double_quant=True
#             )

#             tokenizer = AutoTokenizer.from_pretrained(
#                 llm_model_name
#             )
            
#             model = AutoModelForCausalLM.from_pretrained(
#                 llm_model_name,
#                 quantization_config=quantization_config,
#                 device_map = {"":0},
#                 low_cpu_mem_usage= True
#             )

#             generator = pipeline(
#                 "text-generation",
#                 model=model,
#                 tokenizer=tokenizer,
#                 max_new_tokens=256,
#                 do_sample=False,
#                 temperature=None
#             )

#             self.llm = HuggingFacePipeline(
#                 pipeline=generator
#             )
#         except Exception as e:
#             logger.error(f"LLM initialization failed: {str(e)}")
#             raise RuntimeError(f"LLM initialization failed: {str(e)}. Ensure your token has access to 'meta-llama/Llama-3.1-8B'.")

#         # Define prompt template
#         prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, say so, but don't make up an answer.

#                                 {context}

#                             Question: {question}
#                             Answer: 
#     """

#         # here we are using reusable prompt which takes query and reterieved content which further send to the LLM Model for generating the final output.
#         self.prompt = PromptTemplate(
#             template=prompt_template,
#             input_variables=["context", "question"]
#         )

#         # Create RAG chain
#         def format_docs(docs):
#             return "\n\n".join(doc.page_content for doc in docs)

#         self.qa_chain = RunnableParallel(
#             {
#                 "result": (
#                     {
#                         "context": self.vectorstore.as_retriever(search_kwargs={"k": 3}) | format_docs,
#                         # using Runnable to forward the query to LLM model without any change in it.
#                         "question": RunnablePassthrough()
#                     }
#                     | self.prompt
#                     | self.llm
#                     | StrOutputParser()
#                 ),
#                 # retirieving only top 3 chunks which is more relevant to the user query.
#                 "source_documents": self.vectorstore.as_retriever(search_kwargs={"k": 3})
#             }
#         )

#     def answer_query(self, question):
#         """Answer a query based on the document."""
#         try:
#             if not question.strip():
#                 raise ValueError("Query cannot be empty.")
#             # here it invoking the LLM model with user query and retirieve the content from vectorstore and return the final answer.
#             result = self.qa_chain.invoke(question)
#             return result
#         except Exception as e:
#             logger.error(f"Query error: {str(e)}\n{traceback.format_exc()}")
#             raise RuntimeError(f"Error processing query: {str(e)}")
=======
#             text_splits = self.text_splitter.split_text(self.text)
#             if not text_splits:
#                 logger.error("No text splits generated from document")
#                 raise ValueError("No text could be split from the document.")
#             self.vectorstore.add_texts(text_splits)
#             logger.info("Text split and added to vector store")
#         except Exception as e:
#             logger.error(f"Vector store setup failed: {str(e)}\n{traceback.format_exc()}")
#             raise ValueError(f"Failed to process document: {str(e)}")

#         # QA pipeline initialization
#         try:
#             device = 0 if current_app.config.get('CUDA_AVAILABLE', False) and torch.cuda.is_available() else -1
#             qa_pipeline = pipeline(
#                 "question-answering",
#                 model="deepset/minilm-uncased-squad2",
#                 tokenizer="deepset/minilm-uncased-squad2",
#                 device=device,
#                 max_length=512,
#                 handle_impossible_answer=True
#             )
#             self.llm = CustomHuggingFacePipeline(pipeline=qa_pipeline)
#             logger.info("Initialized QA pipeline with deepset/minilm-uncased-squad2")
#         except Exception as e:
#             logger.error(f"QA pipeline initialization failed: {str(e)}\n{traceback.format_exc()}")
#             raise ValueError(f"QA pipeline initialization failed: {str(e)}")

#         # RetrievalQA setup
#         try:
#             prompt_template = """Context:
# {context}

# Question:
# {question}

# Answer:"""
#             prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
#             self.qa = RetrievalQA.from_chain_type(
#                 llm=self.llm,
#                 chain_type="stuff",
#                 retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
#                 return_source_documents=True,
#                 chain_type_kwargs={"prompt": prompt}
#             )
#             logger.info("Initialized RetrievalQA chain")
#         except Exception as e:
#             logger.error(f"RetrievalQA setup failed: {str(e)}\n{traceback.format_exc()}")
#             raise ValueError(f"RetrievalQA initialization failed: {str(e)}")

#     def _extract_text_from_pdf(self, pdf_path):
#         """Extract text from PDF using pdfplumber, with OCR fallback."""
#         text = ""
#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page in pdf.pages:
#                     page_text = page.extract_text() or ""
#                     text += page_text + "\n"
#             logger.info(f"Extracted text length from PDF: {len(text)} characters")
#         except Exception as e:
#             logger.error(f"PDF text extraction failed: {str(e)}\n{traceback.format_exc()}")

#         if not text.strip():
#             logger.info("Attempting OCR for image-based PDF")
#             try:
#                 with pdfplumber.open(pdf_path) as pdf:
#                     for page_num, page in enumerate(pdf.pages, 1):
#                         img = page.to_image(resolution=300).original
#                         img = img.convert("L")  # Convert to grayscale
#                         page_text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
#                         if page_text.strip():
#                             text += page_text + "\n"
#                         logger.debug(f"OCR page {page_num}: {len(page_text)} characters extracted")
#             except Exception as e:
#                 logger.error(f"OCR extraction failed: {str(e)}\n{traceback.format_exc()}")
#         return text

#     def answer_query(self, query):
#         """Answer a query using the RetrievalQA chain."""
#         if not query or not isinstance(query, str) or not query.strip():
#             logger.error("Query cannot be empty")
#             raise ValueError("Query cannot be empty")
#         try:
#             result = self.qa.invoke({"query": query})
#             logger.info(f"Generated response for query: {query[:50]}...")
#             return result
#         except Exception as e:
#             logger.error(f"Query error: {str(e)}\n{traceback.format_exc()}")
#             raise ValueError(f"Query failed: {str(e)}")








>>>>>>> origin/main





import os
<<<<<<< HEAD
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
=======
import numpy as np
import faiss
import pdfplumber
import logging
import torch
import traceback
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger("langchain_community.vectorstores.faiss").setLevel(logging.WARNING)

class DocumentQA:
    def __init__(self, document, is_pdf=False):
        """Initialize the QA system with a document (text or PDF content)."""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        
        # Set custom cache directory
        cache_dir = "D://huggingface_cache"
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize embeddings
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': self.device}
        encode_kwargs = {'normalize_embeddings': False}
        try:
            self.hf_embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
        except Exception as e:
            logger.error(f"Embedding initialization failed: {str(e)}")
            raise RuntimeError(f"Embedding initialization failed: {str(e)}")

        # Process document
        try:
            if is_pdf:
                # Assume document is a file-like object or path
                with pdfplumber.open(document) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            else:
                text = document
            if not text.strip():
                raise ValueError("No text could be extracted from the document.")
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise RuntimeError(f"Error processing document: {str(e)}")

        # Split text into chunks
        try:
            text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            self.text_split = text_splitter.split_text(text)
            if not self.text_split:
                raise ValueError("Text splitting failed: no documents generated.")
        except Exception as e:
            logger.error(f"Text splitter initialization failed: {str(e)}")
            raise ValueError(f"Text splitter initialization failed: {str(e)}")

        # Create FAISS vectorstore
        try:
            sample_embedding = np.array(self.hf_embeddings.embed_query("sample text"))
            dimension = sample_embedding.shape[0]
            index = faiss.IndexFlatL2(dimension)
            self.vectorstore = FAISS(
                embedding_function=self.hf_embeddings.embed_query,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={}
            )
            self.vectorstore.add_texts(texts=self.text_split)
        except Exception as e:
            logger.error(f"Vector store setup failed: {str(e)}")
            raise RuntimeError(f"Vector store setup failed: {str(e)}")

        # Initialize LLM via Hugging Face Endpoint
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        try:
            self.llm = HuggingFaceEndpoint(
                repo_id="meta-llama/Llama-3.1-8B-Instruct",
                huggingfacehub_api_token=token,
                temperature=0.6,
                provider="hf-inference"
            )
        except Exception as e:
            logger.error(f"LLM initialization failed: {str(e)}")
            raise RuntimeError(f"LLM initialization failed: {str(e)}. Ensure your token has access to 'meta-llama/Llama-3.1-8B'.")

        # Define prompt template
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, say so, but don't make up an answer.

{context}

Question: {question}
Answer: """
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        # Create RAG chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.qa_chain = RunnableParallel(
            {
                "result": (
                    {
                        "context": self.vectorstore.as_retriever(search_kwargs={"k": 3}) | format_docs,
                        "question": RunnablePassthrough()
                    }
                    | self.prompt
                    | self.llm
                    | StrOutputParser()
                ),
                "source_documents": self.vectorstore.as_retriever(search_kwargs={"k": 3})
            }
        )

    def answer_query(self, question):
        """Answer a query based on the document."""
        try:
            if not question.strip():
                raise ValueError("Query cannot be empty.")
            result = self.qa_chain.invoke(question)
            return result
        except Exception as e:
            logger.error(f"Query error: {str(e)}\n{traceback.format_exc()}")
            raise RuntimeError(f"Error processing query: {str(e)}")
>>>>>>> origin/main
