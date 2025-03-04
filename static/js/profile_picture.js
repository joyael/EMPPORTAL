

document.addEventListener('DOMContentLoaded', function() {
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