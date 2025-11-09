/**
 * Profile Visibility Button Management
 *
 * Handles the interaction between two large buttons (Private/Public)
 * and the hidden checkbox that controls the is_public form field
 */

document.addEventListener("DOMContentLoaded", () => {
	const privateBtn = document.getElementById("profile-visibility-private");
	const publicBtn = document.getElementById("profile-visibility-public");
	const hiddenCheckbox = document.getElementById(
		"id_is_public",
	) as HTMLInputElement;

	if (!privateBtn || !publicBtn || !hiddenCheckbox) {
		return;
	}

	/**
	 * Update button states based on checkbox value
	 */
	const updateButtonStates = (): void => {
		const isPublic = hiddenCheckbox.checked;

		const accentClasses = ["btn-accent", "text-accent-content"];
		const baseClasses = ["bg-base-300", "text-base-content/50"];

		if (isPublic) {
			// Public selected
			privateBtn.classList.remove(...accentClasses);
			privateBtn.classList.add(...baseClasses);
			publicBtn.classList.remove(...baseClasses);
			publicBtn.classList.add(...accentClasses);
		} else {
			// Private selected (default)
			privateBtn.classList.remove(...baseClasses);
			privateBtn.classList.add(...accentClasses);
			publicBtn.classList.remove(...accentClasses);
			publicBtn.classList.add(...baseClasses);
		}
	};

	/**
	 * Handle private button click
	 */
	privateBtn.addEventListener("click", (e: Event) => {
		e.preventDefault();
		hiddenCheckbox.checked = false;
		updateButtonStates();
	});

	/**
	 * Handle public button click
	 */
	publicBtn.addEventListener("click", (e: Event) => {
		e.preventDefault();
		hiddenCheckbox.checked = true;
		updateButtonStates();
	});

	// Initialize button states on page load
	updateButtonStates();
});
