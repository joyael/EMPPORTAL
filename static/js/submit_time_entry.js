function gotohome() {
    const button = document.getElementById('cancel_button');
    const homeUrl = button.getAttribute('data-home-url');
    window.location.href = homeUrl;
}


    


document.addEventListener("DOMContentLoaded", function () {

    const dateInputS = document.getElementById('id_date');
    dateInputS.value = '';

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

    const dateInput = document.getElementById('id_date');
    const errorMessage = document.getElementById('errorbox');

    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0]; // Format date as YYYY-MM-DD
    dateInput.setAttribute('max', formattedDate);

    // dateInput.addEventListener('change', function() {
    //     const selectedDate = new Date(dateInput.value);
    //     today.setHours(0, 0, 0, 0); 

    //     if (selectedDate > today) {
    //         errorMessage.textContent = "The date cannot be in the future.";
    //         errorMessage.style.display = 'block';
    //         dateInput.setCustomValidity("The date cannot be in the future."); // Set custom validity
    //     } else {
    //         errorMessage.style.display = 'none'; // Hide error message
    //         dateInput.setCustomValidity(""); // Clear custom validity
    //     }
    // });

    const projectSelect = document.getElementById('id_project');
    const time_entry_form = document.getElementById('employeeForm');
    const fetchProjectsUrl = time_entry_form.getAttribute('data-fetchProjects-url');

    function fetchProjects() {
        console.log("date changed");
        const selectedDate = dateInput.value;
        if (!selectedDate) {
            return; // Exit if no date is selected
        }
        const data = new FormData();
        data.append('date', selectedDate);

        fetch(fetchProjectsUrl, { // Replace with your actual URL
            method: 'POST',
            body: data,
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // To indicate that this is an AJAX request
                'X-CSRFToken': getCookie('csrftoken') // Include CSRF token if required
            }
        })
        .then(response => response.json())
        .then(data => {
            // Clear existing options
            projectSelect.innerHTML = '';

            // Check if there are project choices
            if (data.project_choices) {
                // Populate the select element with new options
                data.project_choices.forEach(choice => {
                    const option = document.createElement('option');
                    option.value = choice[0]; // The value of the option
                    option.textContent = choice[1]; // The display text of the option
                    projectSelect.appendChild(option);
                });
            } else {
                console.error('No project choices received:', data);
            }
        })
        .catch(error => {
            console.error('Error fetching project choices:', error);
        });
    }

    dateInput.addEventListener('change', fetchProjects);

    // Function to get CSRF token (if needed)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if this cookie string begins with the name we want
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
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


    