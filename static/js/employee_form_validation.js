document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("employeeForm");
    const errorBox = document.getElementById("errorbox");

    // Function to display errors
    function displayErrors(errors) {
        errorBox.innerHTML = errors.join("<br>"); // Display errors
        errorBox.style.display = "block"; // Show error box
        errorBox.style.color = "red";
        errorBox.style.marginTop = "10px";
        errorBox.style.marginBottom = "10px";
        errorBox.style.fontSize = "15px";
    }

    form.addEventListener("submit", function(event) {
        errorBox.innerHTML = ""; // Clear previous errors
        errorBox.style.display = "none"; // Hide error box initially

        let errors = [];
        const firstName = document.getElementById("id_first_name").value.trim();
        const lastName = document.getElementById("id_last_name").value.trim();
        const email = document.getElementById("id_email").value.trim();
        const phone = document.getElementById("id_phone").value.trim();
        const password = document.getElementById("id_password_hash").value.trim(); // Get password value

        // Validate first name
        if (firstName === "") {
            errors.push("First name is required.");
        }

        // Validate last name
        if (lastName === "") {
            errors.push("Last name is required.");
        }

        // Validate email format
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            errors.push("Please enter a valid email address.");
        }

        // Validate phone number (digits only)
        const phonePattern = /^\d+$/;
        if (phone && !phonePattern.test(phone)) {
            errors.push("Phone number must contain only digits.");
        }

        // Password validation
        // Initialize password validation flags
        let hasLowerCase = /[a-z]/.test(password);
        let hasUpperCase = /[A-Z]/.test(password);
        let hasSpecialChar = /[!@#$%^&*]/.test(password);
        let hasDigit = /\d/.test(password);
        let isLengthValid = password.length >= 8 && password.length <= 16;

        // Check each criterion and push specific error messages
        if (!hasLowerCase) {
            errors.push("Password must contain at least one lowercase letter.");
        }
        if (!hasUpperCase) {
            errors.push("Password must contain at least one uppercase letter.");
        }
        if (!hasSpecialChar) {
            errors.push("Password must contain at least one special character.");
        }
        if (!hasDigit) {
            errors.push("Password must contain at least one digit.");
        }
        if (!isLengthValid) {
            errors.push("Password must be 8-16 characters long.");
        }

        // If there are errors, prevent form submission and display errors
        if (errors.length > 0) {
            event.preventDefault(); // Prevent form submission
            displayErrors(errors); // Display errors using the function
        }
        window.scrollTo({
            top: 0,
            behavior: 'smooth' // This will create a smooth scrolling effect
        });
    });
});



function gotoemployeelist() {
    const button = document.getElementById('cancel_button');
    const emplistUrl = button.getAttribute('data-emplist-url');
    window.location.href = emplistUrl;
}