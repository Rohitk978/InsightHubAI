document.addEventListener("DOMContentLoaded", () => {
    const typeSelect = document.querySelector("#context_type");
    const fileGroup = document.querySelector("#context-file-input");
    const textGroup = document.querySelector("#context-text-input");

    const fileInput = document.querySelector("#pdf_file");
    const textInput = document.querySelector("#context_text");

    const sourceForm = document.querySelector("#chat-form");
    const sourceButton = document.querySelector("#load-source-button");

    const questionForm = document.querySelector("#question-form");
    const questionInput = document.querySelector("#question");
    const askButton = document.querySelector("#ask-button");

    const conversation = document.querySelector("#conversation");

    function syncSourceFields() {
        if (!typeSelect || !fileGroup || !textGroup) {
            return;
        }

        const useFile = typeSelect.value === "file";

        fileGroup.hidden = !useFile;
        textGroup.hidden = useFile;

        if (fileInput) {
            fileInput.required = useFile;
        }

        if (textInput) {
            textInput.required = !useFile;
        }
    }

    if (typeSelect) {
        typeSelect.addEventListener("change", syncSourceFields);
        syncSourceFields();
    }

    if (sourceForm) {
        sourceForm.addEventListener("submit", (event) => {
            const useFile = typeSelect?.value === "file";

            if (useFile) {
                const file = fileInput?.files?.[0];

                if (!file) {
                    event.preventDefault();

                    window.alert(
                        "Choose a PDF before loading a source. " +
                        "To keep using your current source, ask a question below."
                    );

                    fileInput?.focus();
                    return;
                }

                if (!file.name.toLowerCase().endsWith(".pdf")) {
                    event.preventDefault();

                    window.alert("Please select a PDF file.");
                    fileInput?.focus();
                    return;
                }
            } else {
                if (!textInput?.value.trim()) {
                    event.preventDefault();

                    window.alert(
                        "Paste some text before loading a source."
                    );

                    textInput?.focus();
                    return;
                }
            }

            if (sourceButton) {
                sourceButton.disabled = true;
                sourceButton.textContent = "Loading source...";
                sourceButton.setAttribute("aria-busy", "true");
            }
        });
    }

    if (questionForm && questionInput && askButton) {
        questionForm.addEventListener("submit", (event) => {
            if (!questionInput.value.trim()) {
                event.preventDefault();
                questionInput.focus();
                return;
            }

            const pendingFile =
                typeSelect?.value === "file" &&
                Boolean(fileInput?.files?.length);

            const pendingText =
                typeSelect?.value === "text" &&
                Boolean(textInput?.value.trim());

            if (pendingFile || pendingText) {
                event.preventDefault();

                window.alert(
                    "You have selected a new source. " +
                    "Click Load / Switch Source first."
                );

                sourceButton?.focus();
                return;
            }

            askButton.disabled = true;
            askButton.textContent = "Thinking...";
            askButton.setAttribute("aria-busy", "true");
        });

        questionInput.addEventListener("keydown", (event) => {
            if (
                event.key === "Enter" &&
                !event.shiftKey &&
                !event.isComposing
            ) {
                event.preventDefault();

                if (questionForm.requestSubmit) {
                    questionForm.requestSubmit();
                }
            }
        });
    }

    if (conversation) {
        conversation.scrollTop = conversation.scrollHeight;
    }
});
