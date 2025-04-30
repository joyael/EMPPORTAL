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
function toggle_check_in_status() {
    const checkinButton = document.getElementById('checkinbutton');
    const url = checkinButton.getAttribute('data-toggle-url');
    fetch(url, {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Parse the JSON response
    })
    .then(data => {
        change_checkin_checkout_button(data.is_check_in);
        console.log(`Hours: ${data.hours}, Minutes: ${data.minutes}, Seconds: ${data.seconds}, Time String: ${data.time_string}`);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function makeRed(element){
    element.classList.add('red_color');
    element.classList.remove('green_color');
}

function makeGreen(element){
    element.classList.remove('red_color');
    element.classList.add('green_color');
}

function change_checkin_checkout_button(is_check_in){
    if (is_check_in) {
        const elements_check_in_left = document.getElementsByClassName('semi-circle-left');
        const elements_check_in_right = document.getElementsByClassName('semi-circle-right');
        const elements_check_in_middle_part = document.getElementsByClassName('semicircle-button');
        
        // Update middle part elements
        for (let i = 0; i < elements_check_in_middle_part.length; i++) {
            elements_check_in_middle_part[i].innerHTML = 'CHECK OUT';
            makeRed(elements_check_in_middle_part[i]);
        }
        
        // Apply makeRed to left semicircle elements
        for (let i = 0; i < elements_check_in_left.length; i++) {
            makeRed(elements_check_in_left[i]);  
        }
        
        // Apply makeRed to right semicircle elements
        for (let i = 0; i < elements_check_in_right.length; i++) {
            makeRed(elements_check_in_right[i]);  
        }

    } 
    else {
        const elements_check_in_left = document.getElementsByClassName('semi-circle-left');
        const elements_check_in_right = document.getElementsByClassName('semi-circle-right');
        const elements_check_in_middle_part = document.getElementsByClassName('semicircle-button');
        for (let i = 0; i < elements_check_in_middle_part.length; i++) {
            elements_check_in_middle_part[i].innerHTML = 'CHECK IN';
            makeGreen(elements_check_in_middle_part[i]);
        }
        for (let i = 0; i < elements_check_in_left.length; i++) {
            makeGreen(elements_check_in_left[i]);
        }
        for (let i = 0; i < elements_check_in_right.length; i++) {
            makeGreen(elements_check_in_right[i]);
        }
    }
}

function updateCheckInTime() {
    const checkInTimeElement = document.getElementById('checkintime');
    const elements = document.getElementsByClassName('checkintime');
    const url = checkInTimeElement.getAttribute('data-time_update-url');
    function fetchTimeUpdate() {
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') 
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            change_checkin_checkout_button(data.is_check_in);
            checkInTimeElement.innerHTML = `<p>${data.time_string}</p>`;
            for (let i = 0; i < elements.length; i++) {
                elements[i].innerHTML = `<p>${data.time_string}</p>`;
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }
    setInterval(fetchTimeUpdate, 1000);
}

document.addEventListener('DOMContentLoaded', () => {
    updateCheckInTime();
});