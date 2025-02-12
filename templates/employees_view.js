function gotoemployeecreate() {
    const button = document.getElementById('add_button');
    const empAddUrl = button.getAttribute('data-empadd-url');
    window.location.href = empAddUrl;
}