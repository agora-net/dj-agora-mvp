 
import Toastify from 'toastify-js';
import "toastify-js/src/toastify.css"

declare global {
    interface Window {
        showNotification: (message: string, duration?: number) => void;
    }
}

export const showNotification = (message: string, duration = 3000) => {
    Toastify({
        text: message,
        duration,
        close: true,
        stopOnFocus: true,
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
    }).showToast();
}

// Make the function globally accessible so we can call it from the Django templates
// using the Django message framework.
window.showNotification = showNotification;
