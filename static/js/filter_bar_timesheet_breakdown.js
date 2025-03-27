document.addEventListener('DOMContentLoaded', () => {
    const myoptions = document.querySelectorAll('.filter_options');
    const buttons = document.querySelectorAll('.filter_select_button');
    const inputs = document.querySelectorAll('.filter_input');

        const fromdateInputI = document.getElementById('fromdateInput');
        const todateInputI = document.getElementById('todateInput');

        const filterDateInputfrom = document.getElementById('fromdateforfilter');
        const filterDateInputto = document.getElementById('todateforfilter');

        filterDateInputfrom.value = '';
        filterDateInputto.value = '';
        
        filterDateInputfrom.value = fromdateInputI.value;
        filterDateInputto.value =  todateInputI.value;

    const filters = [];
    // Function to add a student
    function addFilter(button, dropdown, input, form_input) {
        const filter = {
            button: button,
            dropdown: dropdown,
            input: input,
            form_input:form_input
        };
        filters.push(filter);
    }
    // Adding some students
    addFilter('projects_select_button', 'projects_dropdown', 'projects_select_input','project_id');
    addFilter('employees_select_button', 'employees_dropdown', 'employees_select_input','employee_id');

    console.log(filters);


    // Toggle dropdown visibility
    buttons.forEach(mybutton => {
        mybutton.addEventListener('click', (event) => {
            event.stopPropagation();
            mydropdown_id = filters.find(filter => filter.button === event.currentTarget.id).dropdown;
            mydropdown = document.getElementById(mydropdown_id);
            if (!mydropdown){
                mydropdown = document.getElementById('projects_dropdown');
            }
            const isOpen = mydropdown.classList.contains('dropdown_column_active');

            if (isOpen) {
                closeDropdown(mydropdown,mybutton);
            } else {
                closealldropdowns();
                openDropdown(mydropdown,mybutton);
            }
        });
    });

    // Open dropdown
    function openDropdown(mydropdown,mybutton) {
        mydropdown.classList.add('dropdown_column_active');
        mydropdown.classList.remove('dropdown_column_inactive');
        mybutton.classList.add('filter_select_button_down');
    }

    function closealldropdowns(){
        buttons.forEach(mybutton => {
            dropdown_idforthisbutton = filters.find(filter => filter.button === mybutton.id).dropdown;
            if(!dropdown_idforthisbutton){
                dropdown_idforthisbutton = 'projects_dropdown';
            }
            dropdownforthisbutton = document.getElementById(dropdown_idforthisbutton);
            closeDropdown(dropdownforthisbutton,mybutton);
        });
    }

    // Close dropdown
    function closeDropdown(mydropdown,mybutton) {
        mydropdown.classList.add('dropdown_column_inactive');
        mydropdown.classList.remove('dropdown_column_active');
        mybutton.classList.remove('filter_select_button_down');
    }

    // Filter options based on input
    inputs.forEach(myinput => {
        myinput.addEventListener('input', () => {
            const filterValue = myinput.value.toLowerCase();
            mydropdown_id = filters.find(filter => filter.input === event.currentTarget.id).dropdown;
            if(!mydropdown_id){
                mydropdown_id = 'projects_dropdown';
            }
            const myoptions = document.querySelectorAll('#'+ mydropdown_id + ' .filter_options');
            myoptions.forEach(option => {
                const text = option.textContent.toLowerCase();
                if (text.includes(filterValue)) {
                    option.style.display = 'block';
                } else {
                    option.style.display = 'none';
                }
            });
        });
    });


    // Select option from dropdown
    myoptions.forEach(option => {
        option.addEventListener('click', () => {
            console.log("Option clicked is " + option.classList + " value is " + option.dataset.optionValue);
            mybutton_id='';
            if(option.parentElement?.tagName === 'DIV') {
                mybutton_id = filters.find(filter => filter.dropdown === option.parentElement.id).button;
            }
            if(!mybutton_id){
                mybutton_id=('projects_select_button')
            }

            let mybutton = document.getElementById(mybutton_id);
            let dropdown_idforthisbutton = filters.find(filter => filter.button === mybutton.id).dropdown;
            if(!dropdown_idforthisbutton){
                dropdown_idforthisbutton = 'projects_dropdown';
            }
            let dropdownforthisbutton = document.getElementById(dropdown_idforthisbutton);
            mybutton.querySelector('span').textContent = option.textContent;
            closeDropdown(dropdownforthisbutton,mybutton);
            let formInput_id = filters.find(filter => filter.button === mybutton.id).form_input;
            let formInput = document.getElementById(formInput_id);
            console.log("Found form input");
            formInput.value = option.dataset.optionValue;
            console.log("Set " + formInput.id + " to value " + formInput.value);
        });
    });

    // Close dropdown on outside click
    document.addEventListener('click', (event) => {
        buttons.forEach(mybutton => {
            dropdown_idforthisbutton = filters.find(filter => filter.button === mybutton.id).dropdown;
            if(!dropdown_idforthisbutton){
                dropdown_idforthisbutton = 'projects_dropdown';
            }
            dropdownforthisbutton = document.getElementById(dropdown_idforthisbutton);
            if (!mybutton.contains(event.target) && !dropdownforthisbutton.contains(event.target)) {
                closeDropdown(dropdownforthisbutton,mybutton);
            }
        });
    });

    
    const fromdateInputForFilter = document.getElementById('fromdateforfilter');
    const fromdateInput = document.getElementById('fromdateInput');
    fromdateInputForFilter.addEventListener('change', function() {
        const selectedDate = fromdateInputForFilter.value; 
        if (selectedDate !== '') {
            fromdateInput.value = selectedDate;
            console.log('Selected date set to the hidden input:', fromdateInput.value);
        } else {
            console.log('No date selected.');
            fromdateInput.value = '';
        }
    });
    const todateInputForFilter = document.getElementById('todateforfilter');
    const todateInput = document.getElementById('todateInput');
    todateInputForFilter.addEventListener('change', function() {
        const selectedDate = todateInputForFilter.value; 
        if (selectedDate !== '') {
            todateInput.value = selectedDate;
            console.log('Selected date set to the hidden input:', todateInput.value);
        } else {
            console.log('No date selected.');
            todateInput.value = '';
        }
    });


    filterSubmitButton = document.getElementById('filter_search_button');
    filterSubmitButton.addEventListener('click', (event) => {
        
        const employee_id = document.getElementById('employee_id');
        console.log("Employee ID : " + employee_id.value);
        const form = document.getElementById('myFormForFilter');
        const filterSubmitUrl = filterSubmitButton.getAttribute('data-filterSubmit-url');
        const formData = new FormData(form);

        fetch(filterSubmitUrl, { 
            method: 'POST',
            credentials: 'include',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("Full API Response:", data);
        
            if (!data.html || !data.html_p) {
                console.error("Invalid response structure", data);
                return;
            }
        
            document.getElementById('overview_table_data').innerHTML = data.html;
            document.getElementById('id_pagination_div').innerHTML = data.html_p;
        
            let { total_timesheet_time, total_time_available_you, total_time_logged_you, deviation_you, has_deviation_you } = data;
        
            console.log("Received overview_total_data:", total_timesheet_time);
        
            // Get Elements Safely
            const total_timesheet_time_element = document.getElementById('total_timesheet_time');
            const total_time_available_you_element = document.getElementById('total_time_available_you');
            const total_time_logged_element = document.getElementById('total_time_logged_you');
            const deviation_you_element = document.getElementById('deviation_you');
        
            if (!total_timesheet_time_element || !total_time_available_you_element || !total_time_logged_element || !deviation_you_element) {
                console.error("One or more required elements are missing in the DOM.");
                return;
            }
        
            total_timesheet_time_element.innerHTML = total_timesheet_time ?? "0";
            console.log("current value : ",total_timesheet_time_element.value," Needed value : ",total_timesheet_time);
            
            total_time_available_you_element.innerHTML = total_time_available_you ?? "0";
            total_time_logged_element.innerHTML = total_time_logged_you ?? "0";
            deviation_you_element.innerHTML = deviation_you ?? "0";
        
            let topElements = document.getElementsByClassName('boxes_value');
            console.log("Length of the total data in the top box:", topElements.length);

        
            if (topElements.length >= 3) {
                topElements[0].innerText = total_time_available_you !== undefined ? total_time_available_you : "N/A";
                console.log("Top elemnt : ",topElements[0].innerText,"Needed value: ",total_time_available_you)
                topElements[1].innerText = total_time_logged_you !== undefined ? total_time_logged_you : "N/A";
                topElements[2].innerText = deviation_you !== undefined ? deviation_you : "N/A";
        
                if (has_deviation_you) {
                    topElements[2].classList.add('deviation_color');
                    deviation_you_element.classList.add('has-deviation');
                    deviation_you_element.classList.remove('no-deviation');
                } else {
                    topElements[2].classList.remove('deviation_color');
                    deviation_you_element.classList.remove('has-deviation');
                    deviation_you_element.classList.add('no-deviation');
                }
        
                console.log("Updated footer values:", total_timesheet_time, total_time_available_you, total_time_logged_you, deviation_you);
            } else {
                console.error("Not enough elements with class 'boxes_value' found.");
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
                

    });
});

function gotosubmittimeentry() {
    var button = document.getElementById('add_button');
    var submitTimeEntryUrl = button.getAttribute('data-submitTimeEntry-url');
    window.location.href = submitTimeEntryUrl;
}


function gotoupdatetimeentry() {
    var button = document.getElementById('update_button');
    var updateTimeEntryUrl = button.getAttribute('data-updateTimeEntry-url');
    window.location.href = updateTimeEntryUrl;
}

function gotothisurl(url){
    window.location.href = url;
}