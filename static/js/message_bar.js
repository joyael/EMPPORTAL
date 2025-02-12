// Function to show the message bar

function applyMessageBarStyles(element) {
    if (element) {
        element.style.color = 'black';
        element.style.padding = '10px';
        element.style.textAlign = 'center';
        element.style.position = 'absolute';
        headerElement = document.getElementById('header');
        const heightInPixels = getElementHeightInPixels(headerElement);
        element.style.height = heightInPixels === null ? '0' : String(heightInPixels);
        element.style.top = '0';
        element.style.left = '0';
        element.style.right = '0';
        element.style.zIndex = '1000';
        element.style.fontSize = '16px';
        element.style.width = '100%';
        element.style.display = 'flex';
        element.style.justifyContent = 'center';
        element.style.alignItems = 'center';
    }
}

function getElementHeightInPixels(element) {
    if (element) {
        const rect = element.getBoundingClientRect();
        return rect.height; //Returns the height in pixels
    } else {
        console.error('Element not found');
        return null; //Return null if the element is not found
    }
}

function showMessageBar() {
    const messageBar = document.getElementById('message-bar');
    if (messageBar.innerHTML.trim() !== '') {
        applyMessageBarStyles(messageBar);
        messageBar.style.display = 'flex'; // Ensure the message bar is visible

        setTimeout(() => { //  setTimeout function
            messageBar.style.display = 'none';
            console.log("style set to none");
        }, 1000); // Wait for 1 second before hiding 
    }
}

// Call the function to show the message bar
window.onload = showMessageBar;