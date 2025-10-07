 
import Toastify from 'toastify-js';
import "./toastify.css"

declare global {
    interface Window {
        showNotification: (message: string, tags?: string, duration?: number) => void;
    }
}

export const showNotification = (message: string, tags: string = "", duration = 5000) => {

    const tagToTailwindClassMap: { [key: string]: string } = {
        // Map Django message tags to Tailwind CSS classes
        "debug": "bg-base-300 text-base-content",
        "info": "bg-info text-info-content",
        "success": "bg-success text-success-content",
        "warning": "bg-warning text-warning-content",
        "error": "bg-error text-error-content",
    };

    const className = tags.split(" ").map(tag => tagToTailwindClassMap[tag] || tag).join(" ");

    Toastify({
        text: message,
        duration,
        className,
        close: true,
        stopOnFocus: true,
        gravity: "top", // `top` or `bottom`
        position: "right", // `left`, `center` or `right`
    }).showToast();
}

// Make the function globally accessible so we can call it from the Django templates
// using the Django message framework.
window.showNotification = showNotification;
