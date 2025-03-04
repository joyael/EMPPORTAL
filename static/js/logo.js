
function getHeightByClass(className) {
    const elements = document.getElementsByClassName(className);
    if (elements.length > 0) {
        const rect = elements[0].getBoundingClientRect();
        return Math.round(rect.height);
    } else {
        console.error(`No elements found with class name: ${className}`);
        return null;
    }
}

function getWidthByClass(className) {
    const elements = document.getElementsByClassName(className);
    if (elements.length > 0) {
        return elements[0].offsetWidth;
    } else {
        console.error(`No elements found with class name: ${className}`);
        return null;
    }
}

function getHeightOfElement(element) {
    if (element) {
        return element.offsetHeight;
    } else {
        console.error("Invalid element provided.");
        return null;
    }
}

function getWidthOfElement(element) {
    if (element) {
        return element.offsetWidth;
    } else {
        console.error("Invalid element provided.");
        return null;
    }
}


document.addEventListener("DOMContentLoaded", () => {
    let height = getHeightByClass('navbarrowbox');
    let heightT = getHeightByClass('headerrightbox');
    console.log(`Height of the first element with class 'navbarrowbox': ${height}px`);
    height = String(parseInt(height));
    console.log(`Height of the first element with class 'headerrightbox': ${heightT}px`);
    heightT = String(parseInt(heightT));

    const width = getWidthByClass('logobox');
    console.log(`Width of the first element with class 'logobox': ${width}px`);

    const logoimageboxElements = document.getElementsByClassName('logoimagebox');
    if (logoimageboxElements.length > 0) {
        logoimageboxElements[0].style.height = height + 'px';
    }
    const logoimgElements = document.getElementsByClassName('logoimg');
    if (logoimgElements.length > 0) {
        logoimgElements[0].style.height = height + 'px';
    }


    const logoboxElements = document.getElementsByClassName('logobox');
    if (logoboxElements.length > 0) {
        logoboxElements[0].style.height = heightT + 'px';
    }
    
    
});
