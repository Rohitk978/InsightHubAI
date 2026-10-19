# <<<<<<< HEAD


# from flask import Blueprint, request, render_template
# from ..models.chatbot import DocumentQA
# from ..utils.validators import validate_text_input
# import logging
# import os
# from werkzeug.utils import secure_filename

# chatbot_bp = Blueprint("chatbot", __name__)
# logger = logging.getLogger(__name__)

# ALLOWED_EXTENSIONS = {'pdf'}
# UPLOAD_FOLDER = os.path.join('Uploads')

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @chatbot_bp.route("/", methods=["POST"])
# def chat():
#     try:
#         context_type = request.form.get("context_type")
#         question = request.form.get("question")
#         if not validate_text_input(question):
#             logger.error("Invalid or empty question")
#             return render_template("error.html", error="Invalid or empty question"), 400

#         if context_type == "text":
#             context = request.form.get("context_text")
#             if not validate_text_input(context):
#                 logger.error("Invalid or empty context text")
#                 return render_template("error.html", error="Invalid or empty context text"), 400
#             chatbot = DocumentQA(document=context, is_file=False)
#         elif context_type == "file":
#             if 'context_file' not in request.files:
#                 logger.error("No file uploaded")
#                 return render_template("error.html", error="No PDF file uploaded"), 400
            
#             file = request.files['context_file']
#             if file.filename == '':
#                 logger.error("No file selected")
#                 return render_template("error.html", error="No PDF file selected"), 400
            
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#                 file_path = os.path.join(UPLOAD_FOLDER, filename)
#                 try:
#                     file.save(file_path)
#                 except Exception as e:
#                     logger.error(f"Failed to save file: {str(e)}")
#                     return render_template("error.html", error="Failed to save PDF file."), 400
                
#                 try:
#                     chatbot = DocumentQA(document=file_path, is_file=True)
#                 finally:
#                     try:
#                         os.remove(file_path)
#                     except Exception as e:
#                         logger.warning(f"Failed to delete file {file_path}: {str(e)}")
#             else:
#                 logger.error("Invalid file type")
#                 return render_template("error.html", error="Only PDF files are allowed"), 400
#         else:
#             logger.error("Invalid context type")
#             return render_template("error.html", error="Invalid context type"), 400

#         answer = chatbot.answer_query(question)
#         logger.info(f"Chat response generated for question: {question[:50]}...")
#         return render_template("result.html", result=answer["result"], sources=[doc.page_content for doc in answer.get("source_documents", [])], input_type="chat")
    
#     except Exception as e:
#         logger.error(f"Error in chat: {str(e)}")
#         return render_template("error.html", error=f"An error occurred: {str(e)}"), 500

# @chatbot_bp.route("/", methods=["GET"])
# def chat_form():
#     return render_template("chat.html")






























# 2





# from flask import Blueprint, request, render_template
# import logging
# import traceback
# from dotenv import load_dotenv
# import os
# from huggingface_hub import InferenceClient
# import pdfplumber
# from io import BytesIO

# # Load environment variables from .env file
# load_dotenv()

# chatbot_bp = Blueprint("chatbot", __name__)
# logger = logging.getLogger(__name__)

# @chatbot_bp.route("/chat", methods=["GET", "POST"])
# def chat():
#     if request.method == "GET":
#         return render_template("chat.html")
    
#     try:
#         # Validate token
#         token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
#         if not token:
#             raise ValueError("HUGGINGFACE_TOKEN not found in .env file.")
        
#         # # Verify token authenticity
#         # try:
#         #     user = who_am_i(token=token)
#         #     logger.info(f"Authenticated as {user['name']}")
#         # except Exception as auth_e:
#         #     raise ValueError(f"Invalid Hugging Face token: {str(auth_e)}")
        
#         # Get input: PDF or text
#         if 'pdf_file' in request.files and request.files['pdf_file'].filename:
#             pdf_file = request.files['pdf_file']
#             if not pdf_file.filename.lower().endswith('.pdf'):
#                 return render_template("error.html", error="Invalid file format. Please upload a PDF."), 400
#             # Extract text from PDF using pdfplumber
#             with pdfplumber.open(BytesIO(pdf_file.read())) as pdf:
#                 document = ""
#                 for page in pdf.pages:
#                     document += (page.extract_text() or "") + "\n"
#             is_pdf = True
#         elif 'context_text' in request.form and request.form['context_text'].strip():
#             document = request.form['context_text']
#             is_pdf = False
#         else:
#             return render_template("error.html", error="Please provide either a PDF file or text context."), 400
        
#         question = request.form.get("question")
#         if not question or not question.strip():
#             return render_template("error.html", error="Question is required."), 400
        
#         # Initialize InferenceClient
#         client = InferenceClient(
#             model="meta-llama/Llama-3.1-8B-Instruct",
#             token=token
#             # provider="hf-inference"
#         )
        
#         # Construct prompt
#         prompt = f"Context: {document}\nQuestion: {question}\nAnswer:"
        
#         # Query the model
#         answer = client.text_generation(
#             prompt,
#             max_new_tokens=512,
#             temperature=0.7,
#             top_p=0.9,
#             return_full_text=False
#         )
        
#         # Format response
#         response = {
#             "result": answer,
#             "source_documents": [{"page_content": document}] if is_pdf else []
#         }
        
#         return render_template(
#             "result.html",
#             result=response["result"],
#             sources=[doc["page_content"] for doc in response.get("source_documents", [])],
#             input_type="chat"
#         )
    
#     except Exception as e:
#         error_msg = str(e)
#         if "401" in error_msg or "403" in error_msg:
#             error_msg += " Authentication failed. Verify your token at https://huggingface.co/settings/tokens and ensure access to meta-llama/Llama-3.1-8B-Instruct at https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct."
#         elif "404" in error_msg:
#             error_msg += " Model not found. Confirm the model ID or check Hugging Face Inference API status."
#         elif "Provider" in error_msg:
#             error_msg += " Check provider settings at https://hf.co/settings/inference-providers."
#         logger.error(f"Error in chat: {error_msg}\n{traceback.format_exc()}")
#         return render_template(
#             "error.html",
#             error=f"An error occurred: {error_msg}"
#         ), 500



import os
import logging
import traceback
from flask import Blueprint, request, render_template
from io import BytesIO
import pdfplumber
from huggingface_hub import InferenceClient
from ..utils.file_handler import handle_pdf_upload
from __future__ import annotations

import hashlib
import io
import logging
import threading
import uuid

import pdfplumber
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..models.chatbot import get_document_qa

# Suppress pdfplumber and pikepdf debug logging
# Suppress debug logging for pdfplumber, pikepdf, and related modules
for logger_name in logging.root.manager.loggerDict:
    if logger_name.startswith(('pdfplumber', 'pikepdf')):
        logging.getLogger(logger_name).setLevel(logging.WARNING)


chatbot_bp = Blueprint("chatbot", __name__)
logger = logging.getLogger(__name__)


# Conversation history is kept separately for each browser session.
# The document indexes themselves are saved persistently by DocumentQA.
_CHAT_HISTORY = {}
_HISTORY_LOCK = threading.RLock()

MAX_HISTORY_TURNS = 12
MAX_PDF_BYTES = 25 * 1024 * 1024


def _get_chat_id():
    if "insighthub_chat_id" not in session:
        session["insighthub_chat_id"] = uuid.uuid4().hex

    return session["insighthub_chat_id"]


def _get_history():
    chat_id = _get_chat_id()

    with _HISTORY_LOCK:
        return list(_CHAT_HISTORY.get(chat_id, []))


def _clear_history():
    chat_id = _get_chat_id()

    with _HISTORY_LOCK:
        _CHAT_HISTORY[chat_id] = []


def _render_chat(error=None, status=200):
    return (
        render_template(
            "chat.html",
            error=error,
            chat_history=_get_history(),
            active_document_name=session.get(
                "active_document_name"
            ),
            active_document_type=session.get(
                "active_document_type"
            ),
        ),
        status,
    )


def _extract_pdf(pdf_bytes):
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "\n\n".join(
                page.extract_text() or ""
                for page in pdf.pages
            )
    except Exception as exc:
        logger.exception("Could not extract text from PDF")
        raise ValueError(
            "The PDF could not be read. Please upload a valid PDF."
        ) from exc

    if not text.strip():
        raise ValueError(
            "No selectable text was found in the PDF. "
            "Scanned PDFs need OCR before they can be searched."
        )

    return text


@chatbot_bp.route("/chat", methods=["GET", "POST"])
def chat():

    if request.method == "GET":
        return _render_chat()

    action = request.form.get("action", "ask").strip()
    question = request.form.get("question", "").strip()

    # IMPORTANT:
    # Loading a source does not require a question.
    if action not in {"set_source", "ask"}:
        return _render_chat("Invalid chatbot action.", 400)

    if action == "ask" and not question:
        return _render_chat(
            "Please enter a question before clicking Ask.",
            400,
        )

    context_type = request.form.get("context_type", "").strip()
    uploaded_file = request.files.get("pdf_file")
    pasted_text = request.form.get("context_text", "").strip()

    try:
        qa = get_document_qa()

        document_hash = None
        document_text = None
        source_name = None
        source_type = None

       
        if (
            context_type == "file"
            and uploaded_file
            and uploaded_file.filename
        ):
            if not uploaded_file.filename.lower().endswith(".pdf"):
                raise ValueError(
                    "Please select a file with the .pdf extension."
                )

            pdf_bytes = uploaded_file.read(MAX_PDF_BYTES + 1)

            if not pdf_bytes:
                raise ValueError("The selected PDF is empty.")

            if len(pdf_bytes) > MAX_PDF_BYTES:
                raise ValueError(
                    "The PDF exceeds the 25 MB upload limit."
                )

            document_hash = hashlib.sha256(
                pdf_bytes
            ).hexdigest()

            source_name = (
                uploaded_file.filename
                .replace("\\", "/")
                .split("/")[-1]
            )
            source_type = "pdf"

            # Extract and embed only when an index doesn't already exist.
            if not qa.index_exists(document_hash):
                document_text = _extract_pdf(pdf_bytes)

        elif context_type == "text" and pasted_text:

            document_text = pasted_text
            document_hash = qa.make_hash(document_text)

            source_name = "Pasted text"
            source_type = "text"

  
        else:
            document_hash = session.get(
                "active_document_hash"
            )

            if not document_hash:
                raise ValueError(
                    "Please load a PDF or paste text before asking a question."
                )

            source_name = session.get(
                "active_document_name",
                "Active source",
            )
            source_type = session.get(
                "active_document_type",
                "text",
            )

            if not qa.index_exists(document_hash):
                session.pop("active_document_hash", None)
                session.pop("active_document_name", None)
                session.pop("active_document_type", None)

                raise ValueError(
                    "The saved document index is unavailable. "
                    "Please load your source again."
                )

        if not document_hash:
            raise ValueError(
                "Please select a PDF or enter some text."
            )

        previous_hash = session.get("active_document_hash")
        is_new_source = document_hash != previous_hash

     
        if action == "set_source":

            # This creates the index if needed, or reuses the
            # existing persistent index for the same document.
            qa.prepare_document(
                document_hash=document_hash,
                document=document_text,
            )

            if is_new_source:
                _clear_history()

            session["active_document_hash"] = document_hash
            session["active_document_name"] = (
                source_name
                or session.get(
                    "active_document_name",
                    "Active source",
                )
            )
            session["active_document_type"] = (
                source_type
                or session.get(
                    "active_document_type",
                    "text",
                )
            )

            flash(
                "Source loaded successfully. You can now ask "
                "multiple questions without uploading it again.",
                "success",
            )

            # Do not generate an answer during source loading.
            return redirect(url_for("chatbot.chat"))

      
        if is_new_source:
            _clear_history()

        session["active_document_hash"] = document_hash
        session["active_document_name"] = (
            source_name
            or session.get(
                "active_document_name",
                "Active source",
            )
        )
        session["active_document_type"] = (
            source_type
            or session.get(
                "active_document_type",
                "text",
            )
        )

        response = qa.answer_query(
            document_hash=document_hash,
            question=question,
            document=document_text,
        )

        answer = response.get(
            "result",
            "No answer was generated.",
        )

        sources = [
            doc.page_content
            for doc in response.get("source_documents", [])
        ]

        turn = {
            "question": question,
            "answer": answer,
            "sources": sources,
        }

        chat_id = _get_chat_id()

        with _HISTORY_LOCK:
            history = _CHAT_HISTORY.setdefault(chat_id, [])
            history.append(turn)

            # Keep the latest turns to prevent unbounded memory growth.
            del history[:-MAX_HISTORY_TURNS]

        # Render the conversation page, not result.html.
        return _render_chat()

    except ValueError as exc:
        logger.info("Chat validation error: %s", exc)
        return _render_chat(str(exc), 400)

    except Exception:
        logger.exception("Document chatbot request failed")

        return _render_chat(
            "The request failed. Check the Flask terminal for "
            "the full error. If this is the first question, "
            "check the model dependencies and available GPU memory.",
            500,
        )


@chatbot_bp.route("/chat/clear", methods=["POST"])
def clear_chat():
    _clear_history()

    flash(
        "Conversation cleared. Your active source is still available.",
        "success",
    )

    return redirect(url_for("chatbot.chat"))


@chatbot_bp.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        return render_template("chat.html")
    
    try:
        # Validate token
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not token:
            raise ValueError("HUGGINGFACE_TOKEN not found in .env file.")
        
        # Get input: PDF or text
        if request.form.get("context_type") == "file" and 'pdf_file' in request.files:
            filepath = handle_pdf_upload(request, "pdf_file")
            if isinstance(filepath, tuple):
                logger.error(f"PDF upload error: {filepath[0]}")
                return render_template("error.html", error=filepath[0]), 400
            # Extract text from PDF using pdfplumber
            try:
                with pdfplumber.open(filepath) as pdf:
                    document = ""
                    for page in pdf.pages:
                        document += (page.extract_text() or "") + "\n"
                is_pdf = True
                # Clean up the saved file
                os.remove(filepath)
            except Exception as e:
                logger.error(f"Failed to extract text from PDF: {e}")
                return render_template("error.html", error=f"Failed to process PDF: {str(e)}"), 400
        elif request.form.get("context_type") == "text" and request.form.get("context_text", "").strip():
            document = request.form["context_text"]
            is_pdf = False
        else:
            return render_template("error.html", error="Please provide either a PDF file or text context."), 400
        
        question = request.form.get("question")
        if not question or not question.strip():
            return render_template("error.html", error="Question is required."), 400
        
        # Initialize InferenceClient
        client = InferenceClient(
            model="meta-llama/Llama-3.1-8B-Instruct",
            token=token,
            provider="hf-inference"
        )
        
        # Construct prompt
        prompt = f"Context: {document}\nQuestion: {question}\nAnswer:"
        
        # Query the model
        answer = client.text_generation(
            prompt,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            return_full_text=False
        )
        
        # Format response
        response = {
            "result": answer,
            "source_documents": [{"page_content": document}] if is_pdf else []
        }
        
        return render_template(
            "result.html",
            result=response["result"],
            sources=[doc["page_content"] for doc in response.get("source_documents", [])],
            input_type="chat"
        )
    
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "403" in error_msg:
            error_msg += " Authentication failed. Verify your token at https://huggingface.co/settings/tokens and ensure access to meta-llama/Llama-3.1-8B-Instruct."
        elif "404" in error_msg:
            error_msg += " Model not found. Confirm the model ID or check Hugging Face Inference API status."
        logger.error(f"Error in chat: {error_msg}\n{traceback.format_exc()}")
        return render_template(
            "error.html",
            error=f"An error occurred: {error_msg}"
        ), 500



























# 3
# from flask import Blueprint, request, render_template
# import logging
# import traceback
# from dotenv import load_dotenv
# import os
# from huggingface_hub import InferenceClient
# import pdfplumber
# from io import BytesIO

# # Load environment variables from .env file
# load_dotenv()

# chatbot_bp = Blueprint("chatbot", __name__)
# logger = logging.getLogger(__name__)

# @chatbot_bp.route("/", methods=["GET", "POST"])
# def chat():
#     if request.method == "GET":
#         return render_template("chat.html")
    
#     logger.info(f"Request files: {request.files}")
#     logger.info(f"Request form: {request.form}")
    
#     if 'pdf_file' in request.files and request.files['pdf_file'].filename:
#         pdf_file = request.files['pdf_file']
#         if not pdf_file.filename.lower().endswith('.pdf'):
#             return render_template("error.html", error="Invalid file format. Please upload a PDF."), 400
#         with pdfplumber.open(BytesIO(pdf_file.read())) as pdf:
#             document = ""
#             for page in pdf.pages:
#                 document += (page.extract_text() or "") + "\n"
#         is_pdf = True
#     elif 'context_text' in request.form and request.form['context_text'].strip():
#         document = request.form['context_text']
#         is_pdf = False
#     else:
#         return render_template("error.html", error="Please provide either a PDF file or text context."), 400
#     # Proceed with processing
#     try:
        
#         question = request.form.get("question")
#         if not question or not question.strip():
#             return render_template("error.html", error="Question is required."), 400
        
#         # Initialize InferenceClient
#         client = InferenceClient(
#             model="meta-llama/Llama-3.1-8B-Instruct",
#             token=token
#             # provider="hf-inference"
#         )
        
#         # Construct prompt
#         prompt = f"Context: {document}\nQuestion: {question}\nAnswer:"
        
#         # Query the model
#         answer = client.text_generation(
#             prompt,
#             max_new_tokens=512,
#             temperature=0.7,
#             top_p=0.9,
#             return_full_text=False
#         )
        
#         # Format response
#         response = {
#             "result": answer,
#             "source_documents": [{"page_content": document}] if is_pdf else []
#         }
        
#         return render_template(
#             "result.html",
#             result=response["result"],
#             sources=[doc["page_content"] for doc in response.get("source_documents", [])],
#             input_type="chat"
#         )
    
#     except Exception as e:
#         error_msg = str(e)
#         if "401" in error_msg or "403" in error_msg:
#             error_msg += " Authentication failed. Verify your token at https://huggingface.co/settings/tokens and ensure access to meta-llama/Llama-3.1-8B-Instruct at https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct."
#         elif "404" in error_msg:
#             error_msg += " Model not found. Confirm the model ID or check Hugging Face Inference API status."
#         elif "Provider" in error_msg:
#             error_msg += " Check provider settings at https://hf.co/settings/inference-providers."
#         logger.error(f"Error in chat: {error_msg}\n{traceback.format_exc()}")
#         return render_template(
#             "error.html",
#             error=f"An error occurred: {error_msg}"
#         ), 500

