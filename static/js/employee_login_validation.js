document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("loginForm");
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
        const email = document.getElementById("id_email").value.trim();
        // Validate email format
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            errors.push("Please enter a valid email address.");
        }
    
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