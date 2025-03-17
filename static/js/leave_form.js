function gotoleavelist() {
    var button = document.getElementById('cancel_button');
    var url = button.getAttribute('data-leavelist-url');
    window.location.href = url;
}