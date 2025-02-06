function toggleMenu() {
    document.querySelector(".sidebar").classList.toggle("active");
    document.querySelector(".profile_logout_option").classList.remove("show");
}

function toggleSubmenu(event) {
    event.preventDefault();  // Prevent the default anchor behavior
    let submenu = event.target.nextElementSibling;  // Get the submenu
    if (submenu) {
        submenu.classList.toggle("show");
    }
}

function toggleProfileOption(){
    document.querySelector(".profile_logout_option").classList.toggle("show");
    document.getElementById("plm").classList.toggle("show");
}