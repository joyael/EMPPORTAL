function gotocreatedepartment() {
    const depaddUrl = document.getElementById('add_button').getAttribute('data-depadd-url');
    window.location.href = depaddUrl;
}

function redirectToUrl() {
    const deplistUrl = document.getElementById('cancel_button').getAttribute('data-deplist-url');
}