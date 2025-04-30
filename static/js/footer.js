document.addEventListener('DOMContentLoaded', () => {
    function adjustFooter() {
        const footer = document.querySelector('footer');
        const footerHeight = footer.offsetHeight;
        const bodyHeight = document.body.offsetHeight;
        const windowHeight = window.innerHeight;
        console.log("bodyheight : "+bodyHeight+" , windowHeight: "+windowHeight);

        if (bodyHeight < windowHeight) {
            // console.log("bodyheight : "+bodyHeight+" , windowHeight: "+windowHeight);
            footer.style.position = 'fixed';
            footer.style.left = '0'; 
            footer.style.right = '0'; 
            footer.style.bottom = '0'; 
        } 
        else {
            footer.style.position = 'static';
        }
    }

    adjustFooter();
    window.addEventListener('resize', adjustFooter);
});
