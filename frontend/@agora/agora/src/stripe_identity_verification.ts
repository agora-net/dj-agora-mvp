/*
 * Script to retrieve a client secret from the API and start a 
 * Stripe Identity Verification Flow.
 */

import {loadStripe} from '@stripe/stripe-js';
import {z} from 'zod';

import Cookies from 'js-cookie'

import { showNotification } from './notifications';

// Defined in base.html template so we can vary it using the same .env settings
declare const STRIPE_PUBLISHABLE_KEY: string;
declare const AGORA_GET_STRIPE_SESSION_URL: string;

const stripe = await loadStripe(STRIPE_PUBLISHABLE_KEY);

const StripeVerificationResponse = z.object({
    client_secret: z.string().min(1),
});

const disableButton = (button: HTMLButtonElement) => {
    button.disabled = true;
    button.classList.add('btn-disabled', 'cursor-not-allowed', 'opacity-50');
}

const enableButton = (button: HTMLButtonElement) => {
    button.disabled = false;
    button.classList.remove('btn-disabled', 'cursor-not-allowed', 'opacity-50');
}


const startVerificationFlow = async (button: HTMLButtonElement) => {

    disableButton(button);

    if (!stripe) {
        console.error('Stripe.js has not loaded');
        enableButton(button);
        return;
    }

    // https://docs.djangoproject.com/en/5.2/howto/csrf/#setting-the-token-on-the-ajax-request
    const csrftoken = Cookies.get('csrftoken') ?? '';

    const response = await fetch(AGORA_GET_STRIPE_SESSION_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({}),
    });

    if (!response.ok) {
        console.error('Failed to create verification session');
        showNotification("Failed to start verification", "error");
        enableButton(button);
        return;
    }

    const data = await response.json();
    const parsed = StripeVerificationResponse.safeParse(data);

    if (!parsed.success) {
        console.error('Invalid response from server', parsed.error);
        showNotification("Invalid data received", "error");
        enableButton(button);
        return;
    }

    const {client_secret} = parsed.data;

    const {error} = await stripe.verifyIdentity(client_secret);

    if (error) {
        console.error('Error starting verification flow:', error);
        showNotification(error.message ?? 'Something went wrong', "error");
        enableButton(button);
    } else {
        showNotification("Your identity is being processed", "info");
    }
}

window.addEventListener('load', () => {
    const startButton = document.getElementById('start-verification-button');
    if (startButton) {
        startButton.addEventListener('click', (event) => {
            const target = event.target as HTMLButtonElement;
            startVerificationFlow(target);
        });
    } else {
        console.warn('Start Verification button not found');
    }

});