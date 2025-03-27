function gotoupdateleave() {
    // Get the button element
    const updateButton = document.getElementById('update_button');
    // Retrieve the URL from the data attribute
    const url = updateButton.getAttribute('data-updateLeave-url');
    // Redirectto the specified URL
    window.location.href = url;
}

function gotothisurl(url){
    window.location.href = url;
}