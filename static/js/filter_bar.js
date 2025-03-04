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
    addFilter('managers_select_button', 'managers_dropdown', 'managers_select_input','assigning_manager_id');
    addFilter('roles_select_button', 'roles_dropdown', 'roles_select_input','role_for_form');
    addFilter('statuses_select_button', 'statuses_dropdown', 'statuses_select_input','status');

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

    
    const dateInputForFilter = document.getElementById('dateforfilter');
    const dateInput = document.getElementById('dateInput');
    dateInputForFilter.addEventListener('change', function() {
        const selectedDate = dateInputForFilter.value; 
        if (selectedDate !== '') {
            dateInput.value = selectedDate;
            console.log('Selected date set to the hidden input:', dateInput.value);
        } else {
            console.log('No date selected.');
            dateInput.value = '';
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
            document.getElementById('assignations_table_body').innerHTML = data.html;
        })
        .catch(error => {
            console.error('Error:', error);
        });

    });
});
