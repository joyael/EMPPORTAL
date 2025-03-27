document.addEventListener('DOMContentLoaded', () => {
    const myoptions = document.querySelectorAll('.filter_options');
    const buttons = document.querySelectorAll('.filter_select_button');
    const inputs = document.querySelectorAll('.filter_input');

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
        .then(response => response.json()) // Parse the JSON response
        .then(data => {
            console.log(data.html);
            
            // Update the main content and pagination
            document.getElementById('overview_table_data').innerHTML = data.html;
            document.getElementById('id_pagination_div').innerHTML = data.html_p;
        
            // Get the overview_total_data from the JSON response
            let overview_total_data = data.overview_total_data;
            console.log("Received overview_total_data:", overview_total_data);
        
            // Check if data is valid
            if (!overview_total_data) {
                console.error("overview_total_data is missing or undefined.");
            } else {
                let footerElements = document.getElementsByClassName('overview_table_footer_th');
                console.log("Length of the total data in the table footer:", footerElements.length);
        
                if (footerElements.length >= 9) {
                    footerElements[2].innerText = overview_total_data.total_project_hours !== undefined ? overview_total_data.total_project_hours : "N/A";
                    footerElements[3].innerText = overview_total_data.total_bench_hours !== undefined ? overview_total_data.total_bench_hours : "N/A";
                    footerElements[4].innerText = overview_total_data.total_leave_days !== undefined ? overview_total_data.total_leave_days : "N/A";
                    footerElements[5].innerText = overview_total_data.total_training_hours !== undefined ? overview_total_data.total_training_hours : "N/A";
                    footerElements[6].innerText = overview_total_data.total_learning_hours !== undefined ? overview_total_data.total_learning_hours : "N/A";
                    footerElements[7].innerText = overview_total_data.total_total_hours !== undefined ? overview_total_data.total_total_hours : "N/A";
                    footerElements[8].innerText = overview_total_data.total_deviation !== undefined ? overview_total_data.total_deviation : "N/A";

                    if (overview_total_data.total_has_deviation) {
                        footerElements[8].classList.add('has-deviation'); 
                        footerElements[8].classList.remove('no-deviation'); 
                    } else {
                        footerElements[8].classList.remove('has-deviation'); 
                        footerElements[8].classList.add('no-deviation'); 
                    }
        
                    console.log("Updated footer values:", overview_total_data); // Debugging
                } else {
                    console.error("Not enough elements with class 'overview_table_footer_th' found.");
                }
                let topElements = document.getElementsByClassName('boxes_value');
                console.log("Length of the total data in the top box:", topElements.length);
                if (topElements.length >= 7) {
                    topElements[0].innerText = overview_total_data.total_project_hours !== undefined ? overview_total_data.total_project_hours : "N/A";
                    topElements[1].innerText = overview_total_data.total_bench_hours !== undefined ? overview_total_data.total_bench_hours : "N/A";
                    topElements[2].innerText = overview_total_data.total_training_hours !== undefined ? overview_total_data.total_training_hours : "N/A";
                    topElements[3].innerText = overview_total_data.total_learning_hours !== undefined ? overview_total_data.total_learning_hours : "N/A";
                    topElements[4].innerText = overview_total_data.total_leave_days !== undefined ? overview_total_data.total_leave_days : "N/A";
                    topElements[5].innerText = overview_total_data.total_total_hours !== undefined ? overview_total_data.total_total_hours : "N/A";
                    topElements[6].innerText = overview_total_data.total_deviation !== undefined ? overview_total_data.total_deviation : "N/A";

                    if (overview_total_data.total_has_deviation){
                        topElements[6].classList.add('has-deviation-bg');
                    }
                    else{
                        footerElements[6].classList.remove('has-deviation-bg');
                    }
                    console.log("Updated footer values:", overview_total_data); // Debugging
                } else {
                    console.error("Not enough elements with class 'boxes_value' found.");
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
