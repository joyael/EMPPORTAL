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


function sendDate() {
    const selectedDate = document.getElementById('date-selector').value;
    const csrfToken = getCookie('csrftoken');

    const action_element = document.getElementById("date-selector");
    url = action_element.getAttribute('data-change-url');
    console.log("URL is "+ url);

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ date: selectedDate })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();  
    })
    .then(data => {
        console.log(data.html);
        document.getElementById('timeline-container').innerHTML = data.html;
    })
    .catch(error => {
        console.error('Error:', error);
    });

}

document.addEventListener("DOMContentLoaded", function() {
    const dateInputElement = document.getElementById('date-selector');
    dateInputElement.addEventListener('change', function() {
        sendDate();
    });
});