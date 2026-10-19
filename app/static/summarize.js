document.addEventListener("DOMContentLoaded", () => {
    const typeSelect = document.querySelector("#input_type");

    if (!typeSelect) {
        return;
    }

    const groups = {
        text: document.querySelector("#Text-input"),
        url: document.querySelector("#Url-input"),
        pdf: document.querySelector("#file-input")
    };

    const fields = {
        text: document.querySelector("#text"),
        url: document.querySelector("#url"),
        pdf: document.querySelector("#pdf")
    };

    const form = document.querySelector("#summarize-form");
    const button = form?.querySelector('button[type="submit"]');

    function syncFields() {
        const selected = typeSelect.value;

        Object.entries(groups).forEach(([key, group]) => {
            if (group) {
                group.hidden = key !== selected;
            }

            const field = fields[key];

            if (field) {
                field.required = key === selected;
            }
        });
    }

    typeSelect.addEventListener("change", syncFields);
    syncFields();

    if (form) {
        form.addEventListener("submit", (event) => {
            const selected = typeSelect.value;
            const field = fields[selected];

            if (!field) {
                return;
            }

            if (selected === "pdf") {
                const file = field.files?.[0];

                if (!file) {
                    event.preventDefault();

                    window.alert("Please select a PDF file.");
                    field.focus();
                    return;
                }

                if (!file.name.toLowerCase().endsWith(".pdf")) {
                    event.preventDefault();

                    window.alert("Please select a valid PDF.");
                    field.focus();
                    return;
                }
            } else if (!field.value.trim()) {
                event.preventDefault();
                field.focus();
                return;
            }

            if (button) {
                button.disabled = true;
                button.textContent = "Working...";
                button.setAttribute("aria-busy", "true");
            }
        });
    }
});
