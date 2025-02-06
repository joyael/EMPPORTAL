document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const errorBox = document.getElementById("errorbox");

    form.addEventListener("submit", function(event) {

        const departmentName = document.getElementById("id_department_name").value.trim();
        const description = document.getElementById("id_description").value.trim();
        
        // Initialize an array to hold error messages
        let errors = [];

        // Validate Department Name
        if (departmentName === "") {
            errors.push("Department Name is required.");
        } else if (departmentName.length > 100) {
            errors.push("Department Name must be less than 100 characters.");
        }

        // Validate Description
        if (description === "") {
            errors.push("Description is required.");
        } else if (description.length > 1000) {
            errors.push("Department Description must be less than 1000 characters.");
        }

        // If there are errors, prevent form submission and display errors
        if (errors.length > 0) {
            event.preventDefault(); // Prevent form submission
            
            // Clear previous error messages
            errorBox.innerHTML = "";
            errorBox.innerHTML = errors.join("<br>"); // Join errors with line breaks
            errorBox.style.display = "block";
            errorBox.style.color = "red";
            errorBox.style.marginTop = "10px";
            errorBox.style.marginBottom = "10px";
            errorBox.style.fontSize = "15px";

            // Display errors in the error box
            
        } else {
            errorBox.style.display = "none"; // Hide the error box if no errors
            errorBox.className = "errorbox"; 
        }
    });
}) ; 


function redirectToUrl() {
    const deplistUrl = document.getElementById('cancel_button').getAttribute('data-deplist-url');
    window.location.href = deplistUrl;
}