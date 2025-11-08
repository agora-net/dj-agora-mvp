/**
 * Profile Links Dynamic Input Management
 *
 * Handles dynamic addition and removal of profile link input fields
 * Syncs individual inputs to a hidden textarea for form submission
 */

document.addEventListener("DOMContentLoaded", () => {
	const container = document.getElementById("profile-links-container");
	const addBtn = document.getElementById("add-link-btn");
	const hiddenTextarea = document.getElementById(
		"id_profile_links",
	) as HTMLTextAreaElement;

	if (container && addBtn && hiddenTextarea) {
		// Parse initial links from hidden textarea
		const initialLinks = hiddenTextarea.value
			.split("\n")
			.map((link) => link.trim())
			.filter((link) => link.length > 0);

		// Initialize with at least one input
		if (initialLinks.length === 0) {
			addLinkInput("");
		} else {
			initialLinks.forEach((link: string): void => {
				addLinkInput(link);
			});
		}

		// Add new link input
		addBtn.addEventListener("click", () => {
			addLinkInput("");
		});

		// Sync inputs to hidden textarea before form submission
		const form = container.closest("form");
		if (form) {
			form.addEventListener("submit", (): void => {
				const links = Array.from(
					container.querySelectorAll(
						".link-input",
					) as NodeListOf<HTMLInputElement>,
				)
					.map((input) => input.value.trim())
					.filter((value) => value.length > 0);
				hiddenTextarea.value = links.join("\n");
			});
		}

		const addLinkInput = (value = ""): void => {
			const wrapper = document.createElement("div");
			wrapper.className = "flex gap-2";

			const input = document.createElement("input");
			input.type = "url";
			input.className = "link-input input input-bordered flex-1";
			input.placeholder = "https://example.com/profile";
			input.value = value;

			const removeBtn = document.createElement("button");
			removeBtn.type = "button";
			removeBtn.className = "btn btn-square btn-outline btn-error";
			removeBtn.innerHTML = "<span>−</span>";
			removeBtn.onclick = () => {
				// Keep at least one input
				if (container.children.length > 1) {
					wrapper.remove();
				} else {
					input.value = "";
				}
			};

			wrapper.appendChild(input);
			wrapper.appendChild(removeBtn);

			container.appendChild(wrapper);
		};
	}
});
