/* =========================================================
   CIVICCONNECT - GLOBAL JAVASCRIPT
========================================================= */


/* =========================================================
   MOBILE MENU
========================================================= */

function toggleMenu() {
    const menu = document.querySelector(".nav-links");

    if (menu) {
        menu.classList.toggle("show");
    }
}


/* =========================================================
   CLOSE MOBILE MENU WHEN LINK IS CLICKED
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const navLinks = document.querySelectorAll(".nav-links a");

    navLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            const menu = document.querySelector(".nav-links");

            if (menu) {
                menu.classList.remove("show");
            }

        });

    });

});


/* =========================================================
   FLASH MESSAGE AUTO HIDE
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const flashMessages = document.querySelectorAll(".flash");

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);

        }, 5000);

    });

});


/* =========================================================
   IMAGE FILE NAME
========================================================= */

function showFileName(input) {

    const fileNameElement =
        document.getElementById("file-name");

    if (!fileNameElement) {
        return;
    }

    if (input.files && input.files.length > 0) {

        fileNameElement.textContent =
            "Selected file: " + input.files[0].name;

    } else {

        fileNameElement.textContent =
            "No file selected";

    }
}


/* =========================================================
   IMAGE PREVIEW
========================================================= */

function previewImage(input) {

    const preview =
        document.getElementById("image-preview");

    if (!preview) {
        return;
    }

    if (input.files && input.files[0]) {

        const file = input.files[0];

        if (!file.type.startsWith("image/")) {
            preview.style.display = "none";
            return;
        }

        const reader = new FileReader();

        reader.onload = function (event) {

            preview.src = event.target.result;
            preview.style.display = "block";

        };

        reader.readAsDataURL(file);

    } else {

        preview.style.display = "none";

    }
}


/* =========================================================
   FILE SIZE VALIDATION
   Maximum = 5 MB
========================================================= */

function validateFileSize(input) {

    if (!input.files || input.files.length === 0) {
        return true;
    }

    const file = input.files[0];

    const maxSize = 5 * 1024 * 1024;

    if (file.size > maxSize) {

        alert("Image size must be less than 5 MB.");

        input.value = "";

        const preview =
            document.getElementById("image-preview");

        if (preview) {
            preview.style.display = "none";
        }

        return false;
    }

    return true;
}


/* =========================================================
   COMPLAINT IMAGE HANDLER
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const imageInput =
        document.querySelector('input[type="file"]');

    if (imageInput) {

        imageInput.addEventListener("change", function () {

            if (!validateFileSize(this)) {
                return;
            }

            showFileName(this);
            previewImage(this);

        });

    }

});


/* =========================================================
   CONFIRM DELETE / ACTION
========================================================= */

function confirmAction(message) {

    return confirm(
        message || "Are you sure you want to continue?"
    );

}


/* =========================================================
   ROLE CHANGE CONFIRMATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const roleForms =
        document.querySelectorAll(".role-form");

    roleForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const select =
                form.querySelector("select[name='role']");

            if (!select) {
                return;
            }

            const role =
                select.options[select.selectedIndex].text;

            const confirmed = confirm(
                "Are you sure you want to change this user's role to " +
                role +
                "?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

});


/* =========================================================
   STATUS UPDATE CONFIRMATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const updateForms =
        document.querySelectorAll(".update-form");

    updateForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to update this complaint?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

});


/* =========================================================
   SEARCH TABLE
========================================================= */

function searchTable(inputId, tableId) {

    const input =
        document.getElementById(inputId);

    const table =
        document.getElementById(tableId);

    if (!input || !table) {
        return;
    }

    const filter =
        input.value.toLowerCase();

    const rows =
        table.querySelectorAll("tbody tr");

    rows.forEach(function (row) {

        const text =
            row.textContent.toLowerCase();

        if (text.includes(filter)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }

    });

}


/* =========================================================
   PASSWORD SHOW / HIDE
========================================================= */

function togglePassword(inputId, button) {

    const input =
        document.getElementById(inputId);

    if (!input) {
        return;
    }

    if (input.type === "password") {

        input.type = "text";

        if (button) {
            button.textContent = "Hide";
        }

    } else {

        input.type = "password";

        if (button) {
            button.textContent = "Show";
        }

    }

}


/* =========================================================
   CURRENT YEAR
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const yearElements =
        document.querySelectorAll(".current-year");

    yearElements.forEach(function (element) {

        element.textContent =
            new Date().getFullYear();

    });

});


/* =========================================================
   PREVENT DOUBLE FORM SUBMISSION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const forms =
        document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton =
                form.querySelector(
                    'button[type="submit"], input[type="submit"]'
                );

            if (!submitButton) {
                return;
            }

            if (
                submitButton.dataset.noDisable === "true"
            ) {
                return;
            }

            setTimeout(function () {

                submitButton.disabled = true;

                const originalText =
                    submitButton.textContent;

                if (submitButton.tagName === "BUTTON") {

                    submitButton.textContent =
                        "Processing...";

                }

            }, 10);

        });

    });

});