
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

function do_the_change(action){
    const action_element = document.getElementById("action_for_view");
    action_element.value = action;
    url = action_element.getAttribute('data-attendance_tview-url')

    const formElement = document.getElementById("form_for_tabular_view");
    let formData = new FormData(formElement);

    const csrfToken = getCookie('csrftoken');
    fetch(url, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": csrfToken, // CSRF protection
            "Accept": "application/json" // Specify that we expect JSON in response
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok " + response.statusText);
        }
        return response.json(); // Parse the response as JSON
    })
    .then(data => {
        // Update the HTML content of the target element with the received HTML
        document.getElementById("the_attendance_table_wrap_box").innerHTML = data.html;
    })
    .catch(error => {
        console.error("Error:", error);
    });
}  


function previous_calendar_view(){
    action = "previous";
    do_the_change(action);
}

function next_calendar_view(){
    action = "next";
    do_the_change(action);
}

function toggle_week_view(){
    action = "week";
    do_the_change(action);
}

function toggle_month_view(){
    action = "month";
    do_the_change(action);
}