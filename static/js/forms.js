function enableSubmitIfValid(formSelector, submitSelector) {
    const form = document.querySelector(formSelector);
    const submitBtn = form.querySelector(submitSelector);

    function checkForm() {
        let allValid = true;

        form.querySelectorAll("input").forEach(input => {
            // Input is valid if it is not empty and data-valid=true
            if (!input.value  || input.dataset.valid === "false") {
                allValid = false;
            } 
        });

        submitBtn.disabled = !allValid;
    }

    form.querySelectorAll("input").forEach(input => {
        input.addEventListener("input", checkForm);
        input.addEventListener("change", checkForm);
    })
}

enableSubmitIfValid("#signup-form", "#submit-btn");