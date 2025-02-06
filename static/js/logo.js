// Function to get the height of the first element with the specified class name
function getHeightByClass(className) {
    const elements = document.getElementsByClassName(className);
    
    if (elements.length > 0) {
        // Get the full rendered dimensions including CSS transforms
        const rect = elements[0].getBoundingClientRect();
        return Math.round(rect.height); // Returns precise height including transforms
    } else {
        console.error(`No elements found with class name: ${className}`);
        return null;
    }
}

// Function to get the width of the first element with the specified class name
function getWidthByClass(className) {
    // Get the elements by class name
    const elements = document.getElementsByClassName(className);
    
    // Check if any elements were found
    if (elements.length > 0) {
        // Return the width of the first element in pixels
        return elements[0].offsetWidth; // Returns width in pixels
    } else {
        console.error(`No elements found with class name: ${className}`);
        return null; // Return null if no elements found
    }
}

// Function to get the height of a specific element passed as an argument
function getHeightOfElement(element) {
    if (element) {
        return element.offsetHeight; // Returns height in pixels
    } else {
        console.error("Invalid element provided.");
        return null; // Return null if the element is invalid
    }
}

// Function to get the width of a specific element passed as an argument
function getWidthOfElement(element) {
    if (element) {
        return element.offsetWidth; // Returns width in pixels
    } else {
        console.error("Invalid element provided.");
        return null; // Return null if the element is invalid
    }
}

// Example usage
document.addEventListener("DOMContentLoaded", () => {
    // Get height of the first element with class 'headerrightbox'
    let height = getHeightByClass('headerrightbox');
    console.log(`Height of the first element with class 'headerrightbox': ${height}px`);
    height = String(parseInt(height)+5);

    // Get width of the first element with class 'logobox'
    const width = getWidthByClass('logobox');
    console.log(`Width of the first element with class 'logobox': ${width}px`);

    const logoimageboxElements = document.getElementsByClassName('logoimagebox');
    if (logoimageboxElements.length > 0) {
        logoimageboxElements[0].style.height = height + 'px';// Set height with 'px' unit
    }

    // Set the height of the first element with class 'logobox'
    const logoboxElements = document.getElementsByClassName('logobox');
    if (logoboxElements.length > 0) {
        logoboxElements[0].style.height = height + 'px';// Set height with 'px' unit
    }
    

    // Set the height of the first element with class 'logoimg'
    const logoimgElements = document.getElementsByClassName('logoimg');
    if (logoimgElements.length > 0) {
        logoimgElements[0].style.height = height + 'px'; // Set height with 'px' unit
        // logoimgElements[0].style.width = width + 'px'; 
    }
});