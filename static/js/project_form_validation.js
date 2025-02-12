function gotocreateproject() {
    const button = document.getElementById('add_button');
    const projectAddUrl = button.getAttribute('data-projadd-url');
    window.location.href = projectAddUrl;
}
function gotoprojectlist() {
    const button = document.getElementById('cancel_button');
    const projectListUrl = button.getAttribute('data-projadd-url');
    window.location.href = projectAddUrl;
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('projectForm');
    const errorBox = document.getElementById('errorbox'); 

    form.addEventListener('submit', function(event) {
        
        let errors = [];

        const startDate = new Date(document.getElementById('id_start_date').value);
        const endDate = new Date(document.getElementById('id_end_date').value);
        const description = document.getElementById('id_description').value;

        
        if (endDate <= startDate) {
            errors.push('End date must be greater than start date.');
        }

        
        if (description.length > 1000) {
            errors.push('Description must not exceed 1000 characters.');
        }
        if (errors.length > 0) {
            event.preventDefault(); // Prevent form submission
            
            // Clear previous error messages
            errorBox.innerHTML = "";
            errorBox.innerHTML = errors.join("<br>"); // Join errors with line breaks
            errorBox.style.display = "block"; // Show the error box
            errorBox.style.color = "red";
            errorBox.style.marginTop = "10px";
            errorBox.style.marginBottom = "10px";
            errorBox.style.fontSize = "15px";
        } else {
            errorBox.style.display = "none"; // Hide the error box if no errors
        }
    });
});