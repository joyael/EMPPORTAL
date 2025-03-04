document.addEventListener('DOMContentLoaded', () => {
    function adjustFooter() {
        const footer = document.querySelector('footer');
        const footerHeight = footer.offsetHeight;
        const bodyHeight = document.body.offsetHeight;
        const windowHeight = window.innerHeight;
        console.log("bodyheight : "+bodyHeight+" , windowHeight: "+windowHeight);

        if (bodyHeight < windowHeight) {
            console.log("bodyheight : "+bodyHeight+" , windowHeight: "+windowHeight);
            footer.style.position = 'fixed';
            footer.style.left = '0'; // Ensure the footer is aligned to the left
            footer.style.right = '0'; // Ensure the footer is aligned to the right
            footer.style.bottom = '0'; // Position the footer at the bottom
        } 
        else {
            footer.style.position = 'static';
        }
    }

    adjustFooter();
    window.addEventListener('resize', adjustFooter);
});
