

document.addEventListener('DOMContentLoaded', function() {
    const employee_name_div = document.getElementById('employee_name');
    const employee_name_url = employee_name_div.getAttribute('data-emp_name-url');
    if (employee_name_div){
        fetch(employee_name_url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.name) {
                
                employee_name_div.innerHTML = data.name;
            } else {
                
                console.log('No Employee name available.');
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }
    else{
        console.log("No employee name element found");
        
    }
    
    const button = document.getElementById('id_accountbox');
    const profilePictureUrl = button.getAttribute('data-profile_picture-url');
    fetch(profilePictureUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const profilePictureElement = document.querySelector('.account_photo');
            if (data.profile_picture) {
                
                profilePictureElement.src = data.profile_picture;
            } else {
                
                console.log('No profile picture available.');
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

    const profileImageImg = document.getElementById('user_profile_picture_img');
    const profileImageUrl = profileImageImg.getAttribute('data-profile_picture-url');
    if (profileImageImg){
        fetch(profileImageUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.profile_picture) {
                
                profileImageImg.src = data.profile_picture;
            } else {
                
                console.log('No profile picture available.');
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }
    
});