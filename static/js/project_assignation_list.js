function gotocreateprojectassignation() {
    var button = document.getElementById('add_button');
    var url = button.getAttribute('data-projassignadd-url');
    window.location.href = url;
}