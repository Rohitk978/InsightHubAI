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

# Suppress debug logging for pdfplumber, pikepdf, and related modules.
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
