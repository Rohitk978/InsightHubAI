<<<<<<< HEAD
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
=======
const SelectValue = document.getElementById("input_type");
const Text_Input = document.getElementById("Text-input");
const Url_Input = document.getElementById("Url-input");
const File_Input = document.getElementById("file-input");

function handleSelect() {
  const Value = SelectValue.value;

  // Reset all inputs to hidden
  Text_Input.style.display = "none";
  Url_Input.style.display = "none";
  File_Input.style.display = "none";

  // Show the selected input
  if (Value === "text") {
    Text_Input.style.display = "block";
  } else if (Value === "url") {
    Url_Input.style.display = "block";
  } else if (Value === "pdf") {
    File_Input.style.display = "block";
  }
}

// Set initial state on page load
document.addEventListener("DOMContentLoaded", handleSelect);

// Handle dropdown change
SelectValue.addEventListener("change", handleSelect);
>>>>>>> origin/main
