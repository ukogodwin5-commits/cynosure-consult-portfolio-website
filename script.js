document.querySelectorAll(".contact-form").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) return;

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    submitBtn.disabled = true;
    submitBtn.textContent = "Sending...";

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "Accept": "application/json" }
      });

      if (response.ok) {
        alert("Thank you! Your message has been sent successfully.");
        form.reset();
      } else {
        const result = await response.json().catch(() => ({}));
        const errors = result.errors?.map((item) => item.message).join(" ");
        alert(errors || `Formspree rejected the submission (${response.status}). Check the form endpoint.`);
      }
    } catch (error) {
      alert("Could not connect to Formspree. Check your connection and confirm the form endpoint is correct.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
});

const filterButtons = document.querySelectorAll(".filters [data-f]");
const projectCards = document.querySelectorAll(".cases [data-c]");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const selectedFilter = button.dataset.f;

    filterButtons.forEach((filterButton) => {
      const isSelected = filterButton === button;
      filterButton.classList.toggle("on", isSelected);
      filterButton.setAttribute("aria-pressed", String(isSelected));
    });

    projectCards.forEach((card) => {
      card.hidden = selectedFilter !== "all" && card.dataset.c !== selectedFilter;
    });
  });
});