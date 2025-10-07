/*
 * Script to retrieve a client secret from the API and start a 
 * Stripe Identity Verification Flow.
 */

import {loadStripe} from '@stripe/stripe-js';
import {z} from 'zod';

import Cookies from 'js-cookie'

// Defined in base.html template so we can vary it using the same .env settings
declare const STRIPE_PUBLISHABLE_KEY: string;
declare const AGORA_GET_STRIPE_SESSION_URL: string;

const stripe = await loadStripe(STRIPE_PUBLISHABLE_KEY);

const StripeVerificationResponse = z.object({
    client_secret: z.string().min(1),
});


const startVerificationFlow = async () => {
    if (!stripe) {
        console.error('Stripe.js has not loaded');
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
        return;
    }

    const data = await response.json();
    const parsed = StripeVerificationResponse.safeParse(data);

    if (!parsed.success) {
        console.error('Invalid response from server', parsed.error);
        return;
    }

    const {client_secret} = parsed.data;

    const {error} = await stripe.verifyIdentity(client_secret);

    if (error) {
        console.error('Error starting verification flow:', error);
        alert(error.message)
    } else {
        console.log('Verification flow started successfully');
    }
}

window.addEventListener('load', () => {
    const startButton = document.getElementById('start-verification-button');
    if (startButton) {
        startButton.addEventListener('click', startVerificationFlow);
    } else {
        console.warn('Start Verification button not found');
    }

});