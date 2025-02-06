
document.addEventListener("DOMContentLoaded", () => {
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
    
    const csrfToken = getCookie('csrftoken'); // Get the CSRF token from the cookie

    function removeUserActivityEventListeners(){
        ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'].forEach(event => {
            window.removeEventListener(event, userActivityHandler);
        });
    }

    function addUserActivityEventListeners(){
        ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'].forEach(event => {
            window.addEventListener(event, userActivityHandler);
        });
    }
    
    const tokenExpiryTime = 10 * 60 * 1000; 
    let timer;
    let isUserActive = false; 
    let test_iterating_variable=0;
    const refreshUrl = document.getElementById('refreshButton').getAttribute('data-refresh-url'); // Get the URL from the data attribute

    // Refresh token function
    const refreshToken = () => {
        const csrfToken = getCookie('csrftoken'); // Get the CSRF token
        fetch(refreshUrl, {
            method: 'POST',
            credentials: 'include', // Ensures cookies are sent with the request
            headers: {
                'Content-Type': 'application/json', // Set the content type
                'X-CSRFToken': csrfToken // Include the CSRF token
            },
        })
        .then(response => {
            if (response.ok) {
                console.log("Token refreshed successfully.");
            } else {
                console.error("Failed to refresh token.");
            }
        })
        .catch(error => {
            console.error("Error during token refresh:", error);
        });
    };

    // Timer handler to check activity and refresh token if needed
    const handleTimer = () => {
        if (isUserActive) {
            console.log("User was active. Refreshing token...");
            refreshToken(); // Refresh the token if the user was active
        } else {
            console.log("User was not active. Token will not be refreshed.");
        }
        isUserActive = false; // Reset activity flag for the next period
        addUserActivityEventListeners();
        resetTimer(); // Start the next timer
    };


    const resetTimer = () => {
        clearTimeout(timer); // Clear any existing timer
        timer = setTimeout(handleTimer, tokenExpiryTime); // Set a new timer
    };



const userActivityHandler = () => {
    test_iterating_variable += 1;
    isUserActive = true;
    console.log(`User  activity detected ${test_iterating_variable} times`);
};

    
    ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'].forEach(event => {
        window.addEventListener(event, userActivityHandler);
    });

    // Start the initial timer on page load
    resetTimer();
});