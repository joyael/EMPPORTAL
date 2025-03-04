function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function logout() {
    const button = document.getElementById('id_logout_button_o');
    const logoutUrl = button.getAttribute('data-logout-url');
    const loginUrl = button.getAttribute('data-login-url');
    const csrftoken = getCookie('csrftoken'); // Get CSRF token

    fetch(logoutUrl, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken, // Include CSRF token
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            console.log(data.message);
            window.location.href = loginUrl; 
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}