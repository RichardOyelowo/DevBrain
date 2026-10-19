document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) {
        lucide.createIcons();
    }

    const navToggle = document.querySelector("[data-nav-toggle]");
    const navLinks = document.querySelector("[data-nav-links]");
    if (navToggle && navLinks) {
        navToggle.addEventListener("click", () => {
            const expanded = navToggle.getAttribute("aria-expanded") === "true";
            navToggle.setAttribute("aria-expanded", String(!expanded));
            navLinks.classList.toggle("is-open", !expanded);
        });
    }

    const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
    const sidebar = document.querySelector("[data-sidebar]");
    const sidebarBackdrop = document.querySelector("[data-sidebar-backdrop]");

    const closeSidebar = () => {
        sidebar?.classList.remove("is-open");
        sidebarBackdrop?.classList.remove("is-open");
        if (sidebarBackdrop) sidebarBackdrop.hidden = true;
        sidebarToggle?.setAttribute("aria-expanded", "false");
    };

    const openSidebar = () => {
        sidebar?.classList.add("is-open");
        sidebarBackdrop?.classList.add("is-open");
        if (sidebarBackdrop) sidebarBackdrop.hidden = false;
        sidebarToggle?.setAttribute("aria-expanded", "true");
    };

    sidebarToggle?.addEventListener("click", () => {
        if (sidebar?.classList.contains("is-open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    sidebarBackdrop?.addEventListener("click", closeSidebar);

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
