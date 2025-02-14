function gotoassignlist() {
    const button = document.getElementById('cancel_button');
    const assignListUrl = button.getAttribute('data-assignlist-url');
    window.location.href = assignListUrl;
}