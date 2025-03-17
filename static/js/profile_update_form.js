function gotoprofileview() {
    var button = document.getElementById('cancel_button');
    var profileViewUrl = button.getAttribute('data-profileview-url');
    window.location.href = profileViewUrl;
}
document.addEventListener('DOMContentLoaded', function() {
    // Accessing the hidden input elements
var reportingManagerValue = document.getElementById('value_reporting_manager').value;
var roleValue = document.getElementById('value_role').value;
var departmentValue = document.getElementById('value_department').value;
var positionValue = document.getElementById('value_position').value;

var reportingManagerElement = document.getElementById('id_reporting_manager');
var roleElement = document.getElementById('id_role');
var departmentElement = document.getElementById('id_department');
var positionElement = document.getElementById('id_position');

reportingManagerElement.value = reportingManagerValue;
roleElement.value = roleValue;
departmentElement.value = departmentValue;
positionElement.value = positionValue;

});