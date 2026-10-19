<<<<<<< HEAD

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#generate-form");
    const prompt = document.querySelector("#prompt");
    const language = document.querySelector("#target_language");
    const button = document.querySelector("#translate-button");
    const status = document.querySelector("#translation-status");

    if (form && prompt && language && button) {
        form.addEventListener("submit", (event) => {
            if (!prompt.value.trim()) {
                event.preventDefault();
                status.textContent = "Please enter English text.";
                prompt.focus();
                return;
            }

            if (prompt.value.length > 5000) {
                event.preventDefault();
                status.textContent =
                    "Please keep your text within 5,000 characters.";
                return;
            }

            if (!language.value) {
                event.preventDefault();
                status.textContent = "Please select a target language.";
                language.focus();
                return;
            }

            button.disabled = true;
            button.textContent = "Translating...";
            button.setAttribute("aria-busy", "true");

            status.textContent =
                "Checking language and translating your text...";
        });
    }

    const copyButton = document.querySelector("#copy-translation");
    const output = document.querySelector("#translated-output");
    const copyStatus = document.querySelector("#copy-status");

    if (copyButton && output && copyStatus) {
        copyButton.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(output.textContent);
                copyStatus.textContent = "Translation copied successfully.";
            } catch {
                copyStatus.textContent =
                    "Copy failed. Please select and copy the output manually.";
            }
        });
    }
=======
document.addEventListener("DOMContentLoaded", () => {
  console.log("Generate page loaded");
>>>>>>> origin/main
});
