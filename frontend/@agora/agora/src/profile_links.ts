/**
 * Profile Links Dynamic Formset Management
 *
 * Handles dynamic addition and removal of profile link input fields
 * using Django formset management fields to maintain proper form indices
 */

document.addEventListener("DOMContentLoaded", () => {
	const container = document.getElementById("profile-links-container");
	const addBtn = document.getElementById("add-link-btn");
	const emptyFormTemplate = document.getElementById(
		"profile-link-empty-form",
	) as HTMLTemplateElement;

	if (!container || !addBtn || !emptyFormTemplate) {
		return;
	}

	// Get formset management inputs
	const totalFormsInput = document.querySelector(
		'input[name$="-TOTAL_FORMS"]',
	) as HTMLInputElement;

	if (!totalFormsInput) {
		return;
	}

	// Auto-detect formset prefix from management field name
	const prefix = totalFormsInput.name.replace(/-TOTAL_FORMS$/, "");

	/**
	 * Attach remove handler to a link row
	 * Marks the form as deleted and hides the row
	 */
	const attachRemoveHandler = (row: HTMLElement): void => {
		const removeBtn = row.querySelector(
			".remove-link-btn",
		) as HTMLButtonElement;
		if (!removeBtn) {
			return;
		}

		removeBtn.addEventListener("click", (e: Event) => {
			e.preventDefault();

			// Find and check the DELETE checkbox
			const deleteCheckbox = row.querySelector(
				`input[name$="-DELETE"]`,
			) as HTMLInputElement;
			if (deleteCheckbox) {
				deleteCheckbox.checked = true;
			}

			// Hide the row
			row.classList.add("hidden");
		});
	};

	// Initialize remove handlers for existing forms
	document.querySelectorAll(".link-form").forEach((row) => {
		attachRemoveHandler(row as HTMLElement);
	});

	// Add new link handler
	addBtn.addEventListener("click", (e: Event) => {
		e.preventDefault();

		const currentTotal = parseInt(totalFormsInput.value, 10);

		// Clone the empty form template
		const newFormHtml = emptyFormTemplate.innerHTML;

		// Replace __prefix__ with the current form index
		const indexedFormHtml = newFormHtml.replace(
			/__prefix__/g,
			`${currentTotal}`,
		);

		// Create a wrapper div and set its content
		const tempWrapper = document.createElement("div");
		tempWrapper.innerHTML = indexedFormHtml;
		const newRow = tempWrapper.firstElementChild as HTMLElement;

		// Append to container
		container.appendChild(newRow);

		// Refresh icons
		document.dispatchEvent(new CustomEvent("agora:icons:refresh"));

		// Attach remove handler to new row
		attachRemoveHandler(newRow);

		// Increment TOTAL_FORMS
		totalFormsInput.value = `${currentTotal + 1}`;

		// Focus the new input field
		const newInput = newRow.querySelector(
			`input[name$="-url"]`,
		) as HTMLInputElement;
		if (newInput) {
			newInput.focus();
		}
	});
});
