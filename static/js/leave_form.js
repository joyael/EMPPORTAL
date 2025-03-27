function gotoleavelist() {
    var button = document.getElementById('cancel_button');
    var url = button.getAttribute('data-leavelist-url');
    window.location.href = url;
}

function gotoapproveleave() {
    const url = document.getElementById('approve_leave_button').getAttribute('data-approveleave-url');
    // Perform an AJAX request or redirect to the URL
    window.location.href = url; // Redirect to the approve URL
}

function gotorejectleave() {
    const url = document.getElementById('reject_leave_button').getAttribute('data-rejectleave-url');
    // Perform an AJAX request or redirect to the URL
    window.location.href = url; // Redirect to the reject URL
}

function gotocancel() {
    const elemnt = document.getElementById('cancel_leave_button');
    const url = elemnt.getAttribute('data-cancelleave-url');
    console.log("This js function is working ");
    console.log(url); 
    window.location.href = url; 
}