document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector("#nav-links");

    if (toggle && nav) {
        toggle.addEventListener("click", () => {
            const isOpen = nav.classList.toggle("open");

            toggle.setAttribute(
                "aria-expanded",
                String(isOpen)
            );
        });
    }
});