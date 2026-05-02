document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.querySelector("[data-nav-toggle]");
    const navLinks = document.querySelector("[data-nav-links]");
    if (navToggle && navLinks) {
        navToggle.addEventListener("click", () => {
            const expanded = navToggle.getAttribute("aria-expanded") === "true";
            navToggle.setAttribute("aria-expanded", String(!expanded));
            navLinks.classList.toggle("is-open", !expanded);
        });
    }

    const form = document.querySelector("[data-quiz-form]");
    if (!form) return;

    const optionInput = form.querySelector("[data-option-input]");
    const nextButton = form.querySelector("[data-next-button]");
    const feedback = form.querySelector("[data-feedback]");
    const buttons = form.querySelectorAll(".users_answer");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            optionInput.value = button.dataset.optionId;
            buttons.forEach((item) => {
                item.disabled = true;
                if (item.dataset.correct === "true") {
                    item.classList.add("answer-correct");
                }
            });
            if (button.dataset.correct !== "true") {
                button.classList.add("answer-wrong");
            }
            feedback.hidden = false;
            nextButton.hidden = false;
            nextButton.focus();
        });
    });
});
