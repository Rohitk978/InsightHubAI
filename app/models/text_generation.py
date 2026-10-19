import logging
import re

import torch
from langdetect import detect_langs, DetectorFactory, LangDetectException
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

# Make langdetect deterministic
DetectorFactory.seed = 0

MODEL_NAME = "facebook/nllb-200-distilled-600M"
MAX_INPUT_CHARS = 5000

SUPPORTED_LANGUAGES = {
    "Hindi": "hin_Deva",
    "Japanese": "jpn_Jpan",
    "French": "fra_Latn",
    "German": "deu_Latn",
    "Spanish": "spa_Latn",
    "Punjabi": "pan_Guru",
    "Gujarati": "guj_Gujr",
    "Urdu": "urd_Arab",
    "Bengali": "ben_Beng",
    "Marathi": "mar_Deva",
    "Tamil": "tam_Taml",
    "Telugu": "tel_Telu",
    "Chinese (Simplified)": "zho_Hans",
    "Arabic": "arb_Arab",
    "Korean": "kor_Hang",
    "Russian": "rus_Cyrl",
    "Portuguese": "por_Latn",
    "Italian": "ita_Latn",
    "Dutch": "nld_Latn",
    "English": "eng_Latn",
}

LANGUAGE_ERROR = "Language not detected. Please enter text in English."

# Very common English words. langdetect is unreliable on short text
# (it often labels English as Danish/Norwegian/Dutch), so this list is
# used as a second opinion.
ENGLISH_COMMON_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know",
    "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come",
    "its", "over", "think", "also", "back", "after", "use", "two", "how",
    "our", "work", "first", "well", "way", "even", "new", "want",
    "because", "any", "these", "give", "day", "most", "us", "is", "are",
    "was", "were", "am", "has", "had", "been", "hello", "hi", "thanks",
    "thank", "please", "where", "why", "need", "love", "help", "going",
    "today", "name", "fine", "morning", "friend", "yes", "very", "much",
    "here", "more", "many", "should", "does", "did", "don't", "i'm",
}


class TextTranslator:
    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.max_input_chars = MAX_INPUT_CHARS
        self.chunk_tokens = 200

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------
    @staticmethod
    def _english_word_ratio(text):
        words = re.findall(r"[a-zA-Z']+", text.lower())
        if not words:
            return 0.0
        hits = sum(1 for word in words if word in ENGLISH_COMMON_WORDS)
        return hits / len(words)

    def detect_english(self, text):
        cleaned_text = text.strip()

        letters = re.findall(r"[^\W\d_]", cleaned_text)
        latin_letters = re.findall(r"[A-Za-z]", cleaned_text)

        if len(latin_letters) < 3:
            return False

        # Reject text written mostly in non-Latin scripts
        if len(latin_letters) / max(len(letters), 1) < 0.8:
            return False

        word_count = len(re.findall(r"[A-Za-z']+", cleaned_text))
        ratio = self._english_word_ratio(cleaned_text)

        try:
            predictions = detect_langs(cleaned_text)
        except LangDetectException:
            logger.warning("langdetect failed; using word-list check only.")
            return ratio >= 0.2

        logger.info(
            "Language detection results: %s | english word ratio: %.2f",
            predictions,
            ratio,
        )

        best = predictions[0] if predictions else None
        en_prob = next(
            (p.prob for p in predictions if p.lang == "en"), 0.0
        )

        # 1. langdetect clearly says English
        if best is not None and best.lang == "en" and best.prob >= 0.35:
            return True

        # 2. English appears with a reasonable probability
        if en_prob >= 0.15:
            return True

        # 3. langdetect is unreliable on short text, so trust the
        #    common-word check there.
        if word_count < 8:
            return ratio >= 0.2

        # 4. Longer text: require a strong English word signal
        return ratio >= 0.3

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------
    def _load_model(self):
        if self.model is not None:
            return

        logger.info("Loading NLLB translation model: %s", self.model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            src_lang="eng_Latn",
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()

        logger.info("NLLB model loaded on %s", self.device)

    # ------------------------------------------------------------------
    # Chunking (sentence-aware so translations stay coherent)
    # ------------------------------------------------------------------
    def _token_count(self, text):
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def _split_long_sentence(self, sentence):
        token_ids = self.tokenizer.encode(sentence, add_special_tokens=False)
        pieces = []

        for start in range(0, len(token_ids), self.chunk_tokens):
            piece = self.tokenizer.decode(
                token_ids[start:start + self.chunk_tokens],
                skip_special_tokens=True,
            ).strip()
            if piece:
                pieces.append(piece)

        return pieces

    def _make_chunks(self, text):
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+|\n+", text)
            if s.strip()
        ]

        chunks = []
        current = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self._token_count(sentence)

            if sentence_tokens > self.chunk_tokens:
                if current:
                    chunks.append(" ".join(current))
                    current, current_tokens = [], 0
                chunks.extend(self._split_long_sentence(sentence))
                continue

            if current_tokens + sentence_tokens > self.chunk_tokens:
                chunks.append(" ".join(current))
                current, current_tokens = [], 0

            current.append(sentence)
            current_tokens += sentence_tokens

        if current:
            chunks.append(" ".join(current))

        return chunks

    # ------------------------------------------------------------------
    # Translation
    # ------------------------------------------------------------------
    def translate(self, text, target_language):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Please enter English text.")

        text = text.strip()

        if len(text) > self.max_input_chars:
            raise ValueError("Please keep your text within 5,000 characters.")

        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError("Please select a supported target language.")

        if not self.detect_english(text):
            raise ValueError(LANGUAGE_ERROR)

        self._load_model()

        target_code = SUPPORTED_LANGUAGES[target_language]
        target_token_id = self.tokenizer.convert_tokens_to_ids(target_code)

        if target_token_id == self.tokenizer.unk_token_id:
            raise ValueError(
                "The selected language code is not supported by this model."
            )

        chunks = self._make_chunks(text)
        translations = []

        try:
            for index, chunk in enumerate(chunks, start=1):
                inputs = self.tokenizer(
                    chunk,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                with torch.inference_mode():
                    output_ids = self.model.generate(
                        **inputs,
                        forced_bos_token_id=target_token_id,
                        max_new_tokens=400,
                        num_beams=4,
                        do_sample=False,
                    )

                translated = self.tokenizer.decode(
                    output_ids[0],
                    skip_special_tokens=True,
                ).strip()

                if translated:
                    translations.append(translated)

                logger.info("Translated chunk %d/%d", index, len(chunks))

            if not translations:
                raise RuntimeError("No translated text was produced.")

            return "\n\n".join(translations)

        except Exception as exc:
            logger.exception("Translation failed")
            raise RuntimeError(
                "Translation failed. Check the application logs."
            ) from exc
