function previous_calendar_view(){
    action = "previous";
    do_the_change(action);
}

function next_calendar_view(){
    action = "next";
    do_the_change(action);
}

function toggle_week_view(){
    action = "week";
    do_the_change(action);
}

function toggle_month_view(){
    action = "month";
    do_the_change(action);
}

function do_the_change(action){
    const action_element = document.getElementById("action_for_view");
    action_element.value = action;

    let formData = $("#form_for_tabular_view").serialize();
    formData += "&action_for_view=" + action;

    $.ajax({
        type: "POST",
        url: "{% url 'attendance_tabular_view' %}", // Replace with your actual URL
        data: formData,
        dataType: "html",
        headers: { "X-CSRFToken": "{{ csrf_token }}" }, // CSRF protection
        success: function (response) {
            $("#attendance_container").html(response);
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
        }
    });
}