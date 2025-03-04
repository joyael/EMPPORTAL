function gotohome() {
    const button = document.getElementById('cancel_button');
    const homeUrl = button.getAttribute('data-home-url');
    window.location.href = homeUrl;
}

document.addEventListener("DOMContentLoaded", function () {

    let taskIdP = document.querySelector('p:has(#id_task_id)');

    if (taskIdP) {
        taskIdP.style.display = "none";

        let newP = document.createElement("p");
        newP.innerHTML = `
            <label for="task-id">Task ID?</label>
            <select id="task-id" name="task-id">
                <option value="no">No</option>
                <option value="yes">Yes</option>
            </select>
        `;

        taskIdP.parentNode.insertBefore(newP, taskIdP);

        let taskIdSelect = document.getElementById("task-id");
        taskIdSelect.addEventListener("change", function () {
            if (this.value === "yes") {
                taskIdP.style.display = "block"; 
            } else {
                taskIdP.style.display = "none";
            }
        });
    }
    
    // Select the three <p> tags
    let hoursP = document.querySelector('p:has(#id_hours)');
    let minutesP = document.querySelector('p:has(#id_minutes)');
    let secondsP = document.querySelector('p:has(#id_seconds)');

    // Create a div container to wrap them
    let timeContainer = document.createElement("div");
    timeContainer.classList.add("time-container"); // Add a class for styling

    // Append the <p> elements to the container
    if (hoursP && minutesP && secondsP) {
        hoursP.parentNode.insertBefore(timeContainer, hoursP);
        timeContainer.appendChild(hoursP);
        timeContainer.appendChild(minutesP);
        timeContainer.appendChild(secondsP);
    }
});


document.getElementById('employeeForm').addEventListener('submit', function(event) {
    // Get the description input
    const descriptionInput = document.getElementById('id_description');
    const descriptionLength = descriptionInput.value.length;

    // Check if the description exceeds 1000 characters
    if (descriptionLength > 1000) {
        // Prevent form submission
        event.preventDefault();

        // Display an error message
        let message = 'Description must be less than 1000 characters. Current length: ' + descriptionLength;
        const errorBox = document.getElementById('errorbox');
        errorBox.innerHTML = message;
        descriptionInput.focus(); // Set focus back to the description input
    }
});
