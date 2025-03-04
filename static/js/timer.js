// Function to update the current date and time
function updateDateTime() {
    const now = new Date(); 
    
    const year = now.getFullYear(); 
    const month = String(now.getMonth() + 1).padStart(2, '0'); // 2-digit month (0-11, so add 1)
    const day = String(now.getDate()).padStart(2, '0'); // 2-digit day
    let hour = now.getHours(); // 24-hour format
    const minute = String(now.getMinutes()).padStart(2, '0'); // 2-digit minute
    const second = String(now.getSeconds()).padStart(2, '0'); // 2-digit second

    // Determine AM or PM
    const ampm = hour >= 12 ? 'PM' : 'AM';
    hour = hour % 12; // Convert to 12-hour format
    hour = hour ? String(hour).padStart(2, '0') : '12'; // If hour is 0, set it to 12

    // Format the strings
    const dateString = `${day}-${month}-${year}`; // "DD-MM-YYYY"
    const timeString = `${hour}:${minute}:${second} ${ampm}`; // "HH:MM:SS AM/PM"

    // Get the day of the week
    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const dayOfWeek = daysOfWeek[now.getDay()]; // Get the current day name


    const dateTimeBoxes = document.querySelectorAll('.dateTimeBox');
    dateTimeBoxes.forEach(dateTimeBox => {
        const dateElement = dateTimeBox.querySelector('.date');
        const dayElement = dateTimeBox.querySelector('.day');
        const timeElement = dateTimeBox.querySelector('.time');

        if (dateElement) dateElement.textContent = dateString; 
        if (dayElement) dayElement.textContent = dayOfWeek;   
        if (timeElement) timeElement.textContent = timeString;
    });

}

document.addEventListener('DOMContentLoaded', () => {
    updateDateTime();
    setInterval(updateDateTime, 1000);
});