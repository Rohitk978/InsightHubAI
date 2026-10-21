from flask import Blueprint, request, render_template

from ..models.text_generation import (
    TextTranslator,
    SUPPORTED_LANGUAGES,
    MAX_INPUT_CHARS,
)
from ..utils.logger import setup_logger

text_generation_bp = Blueprint("text_generation", __name__)
logger = setup_logger()

# One shared instance so the model is loaded only once
translator = TextTranslator()


def render_translation_form(
    prompt="",
    selected_language="",
    error=None,
    translated_text=None,
    status=200,
):
    return (
        render_template(
            "generate.html",
            languages=list(SUPPORTED_LANGUAGES.keys()),
            prompt=prompt,
            selected_language=selected_language,
            error=error,
            translated_text=translated_text,
        ),
        status,
    )


@text_generation_bp.route("/generate", methods=["GET", "POST"])
def generate():
    if request.method == "GET":
        return render_translation_form()

    prompt = request.form.get("prompt", "").strip()
    target_language = request.form.get("target_language", "").strip()

    if not prompt:
        return render_translation_form(
            prompt=prompt,
            selected_language=target_language,
            error="Please enter English text.",
            status=400,
        )

    if len(prompt) > MAX_INPUT_CHARS:
        return render_translation_form(
            prompt=prompt,
            selected_language=target_language,
            error="Please keep your text within 5,000 characters.",
            status=400,
        )

    if target_language not in SUPPORTED_LANGUAGES:
        return render_translation_form(
            prompt=prompt,
            selected_language=target_language,
            error="Please select a supported target language.",
            status=400,
        )

    try:
        translated_text = translator.translate(prompt, target_language)

        return render_translation_form(
            prompt=prompt,
            selected_language=target_language,
            translated_text=translated_text,
        )

    except ValueError as exc:
        logger.warning("Translation input rejected: %s", exc)

        return render_translation_form(
            prompt=prompt,
            selected_language=target_language,
            error=str(exc),
            status=400,
        )

    except Exception:
        logger.exception("Translation failed")

        return render_translation_form(
            prompt=prompt,
            selected_language=target_language,
            error="Translation failed. Please check the terminal logs.",
            status=500,
        ) 
