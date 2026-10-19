from .utils import load_model, load_tokenizer
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import os
import logging

logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.max_words = 6000
        self.max_file_size_mb = 5
        self.max_input_tokens = 700

    def _load_model(self):
        if self.model is None:
            self.model = load_model(
                "summarization",
                self.model_name
            )

            self.tokenizer = getattr(
                self.model,
                "tokenizer",
                None
            )

            if self.tokenizer is None:
                self.tokenizer = load_tokenizer(
                    self.model_name
                )

            if self.tokenizer is None:
                raise ValueError(
                    "Failed to load the summarization tokenizer."
                )

            logger.info(
                "Loaded summarization model: %s",
                self.model_name
            )

    def _make_chunks(self, text):
        token_ids = self.tokenizer(
            text,
            add_special_tokens=False,
            truncation=False
        )["input_ids"]

        chunks = []

        for start in range(
            0, len(token_ids), self.max_input_tokens
        ):
            chunk_ids = token_ids[
                start:start + self.max_input_tokens
            ]

            chunk = self.tokenizer.decode(
                chunk_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            ).strip()

            if chunk:
                chunks.append(chunk)

        return chunks

    def summarize_text(
        self,
        text,
        max_length=120,
        min_length=30
    ):
        self._load_model()

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text cannot be empty.")

        words = text.split()

        if len(words) > self.max_words:
            text = " ".join(words[:self.max_words])
            logger.warning(
                "Text truncated to %s words",
                self.max_words
            )

        chunks = self._make_chunks(text)

        if not chunks:
            raise ValueError(
                "No valid text chunks were generated."
            )

        summaries = []

        for index, chunk in enumerate(chunks, start=1):
            try:
                input_length = len(
                    self.tokenizer(
                        chunk,
                        add_special_tokens=True,
                        truncation=False
                    )["input_ids"]
                )

                if input_length < 5:
                    continue

                output_max = min(
                    max_length,
                    max(20, int(input_length * 0.4))
                )

                output_min = min(
                    min_length,
                    max(5, output_max - 5)
                )

                result = self.model(
                    chunk,
                    max_length=output_max,
                    min_length=output_min,
                    do_sample=False,
                    num_beams=2,
                    truncation=True
                )

                summary = result[0]["summary_text"].strip()

                if summary:
                    summaries.append(summary)

                logger.info(
                    "Summarized chunk %s/%s",
                    index,
                    len(chunks)
                )

            except Exception:
                logger.exception(
                    "Failed on chunk %s/%s",
                    index,
                    len(chunks)
                )
                raise

        if not summaries:
            raise ValueError(
                "No summaries were generated."
            )

        return " ".join(summaries)

    def summarize_url(
        self,
        url,
        max_length=120,
        min_length=30
    ):
        try:
            response = requests.get(
                url,
                timeout=15,
                headers={
                    "User-Agent": os.getenv(
                        "USER_AGENT",
                        "Mozilla/5.0 (compatible; InsightHub-AI/1.0)"
                    )
                }
            )
            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            for element in soup([
                "script", "style", "nav", "header",
                "footer", "aside", "form"
            ]):
                element.decompose()

            main = (
                soup.find("main")
                or soup.find("article")
                or soup.body
            )

            if main is None:
                raise ValueError(
                    "No main webpage content was found."
                )

            elements = main.find_all(
                ["h1", "h2", "h3", "p", "li"]
            )

            text = "\n".join(
                element.get_text(" ", strip=True)
                for element in elements
                if element.get_text(" ", strip=True)
            )

            if not text.strip():
                raise ValueError(
                    "No meaningful text extracted from URL."
                )

            logger.info(
                "Extracted %s words from URL: %s",
                len(text.split()),
                url
            )

            return self.summarize_text(
                text,
                max_length=max_length,
                min_length=min_length
            )

        except requests.RequestException as exc:
            logger.exception(
                "Failed to fetch URL: %s",
                url
            )
            raise ValueError(
                f"Failed to fetch URL: {exc}"
            ) from exc

    def summarize_pdf(
        self,
        filepath,
        max_length=120,
        min_length=30
    ):
        file_size_mb = (
            os.path.getsize(filepath) / (1024 * 1024)
        )

        if file_size_mb > self.max_file_size_mb:
            raise ValueError(
                f"PDF too large ({file_size_mb:.2f} MB). "
                f"Maximum allowed: {self.max_file_size_mb} MB."
            )

        reader = PdfReader(filepath)
        pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        text = "\n".join(pages)

        if not text.strip():
            raise ValueError("No text extracted from PDF.")

        return self.summarize_text(
            text,
            max_length=max_length,
            min_length=min_length
        )
