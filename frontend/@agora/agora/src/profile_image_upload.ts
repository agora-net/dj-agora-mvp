/**
 * Profile Image Upload Handler
 *
 * Handles drag/drop, file selection, preview, and delete functionality
 * for profile image uploads.
 */

document.addEventListener("DOMContentLoaded", () => {
	const fileInput = document.getElementById(
		"id_profile_image",
	) as HTMLInputElement;
	const dropZone = document.getElementById(
		"profile-image-dropzone",
	) as HTMLElement;
	const previewContainer = document.getElementById(
		"profile-image-preview",
	) as HTMLElement;
	const previewImage = document.getElementById(
		"profile-image-preview-img",
	) as HTMLImageElement;
	const deleteBtn = document.getElementById(
		"profile-image-delete-btn",
	) as HTMLButtonElement;
	const replaceBtn = document.getElementById(
		"profile-image-replace-btn",
	) as HTMLButtonElement;
	const deleteInput = document.getElementById(
		"delete_profile_image",
	) as HTMLInputElement;
	const existingImageContainer = document.getElementById(
		"profile-image-existing",
	) as HTMLElement;

	if (!fileInput || !dropZone || !previewContainer) {
		return;
	}

	const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
	const ALLOWED_TYPES = [
		"image/jpeg",
		"image/png",
		"image/webp",
		"image/heic",
		"image/heif",
		"image/jxl", // JPEG XL
		"image/jp2", // JPEG 2000
	];

	/**
	 * Validate file
	 */
	const validateFile = (file: File): string | null => {
		if (!ALLOWED_TYPES.includes(file.type)) {
			return "Unsupported image format. Allowed: JPEG, PNG, WebP, HEIC, JPEGXL, JPEG2000.";
		}
		if (file.size > MAX_FILE_SIZE) {
			return "Image file too large. Maximum size is 5MB.";
		}
		return null;
	};

	/**
	 * Show preview of selected image
	 */
	const showPreview = (file: File): void => {
		const reader = new FileReader();
		reader.onload = (e: ProgressEvent<FileReader>) => {
			if (e.target?.result && previewImage) {
				const imageSrc = e.target.result as string;
				// Show crop modal first
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				if ((window as any).showProfileImageCrop) {
					// eslint-disable-next-line @typescript-eslint/no-explicit-any
					(window as any).showProfileImageCrop(imageSrc);
				} else {
					// Fallback: show preview directly if crop modal not available
					previewImage.src = imageSrc;
					previewContainer.classList.remove("hidden");
					if (existingImageContainer) {
						existingImageContainer.classList.add("hidden");
					}
					if (dropZone) {
						dropZone.classList.add("hidden");
					}
					if (deleteInput) {
						deleteInput.checked = false;
					}
				}
			}
		};
		reader.readAsDataURL(file);
	};

	/**
	 * Handle file selection
	 */
	const handleFileSelect = (file: File): void => {
		const error = validateFile(file);
		if (error) {
			alert(error);
			return;
		}

		const dataTransfer = new DataTransfer();
		dataTransfer.items.add(file);
		fileInput.files = dataTransfer.files;

		showPreview(file);
	};

	/**
	 * Prevent default drag behaviors
	 */
	const preventDefaults = (e: DragEvent): void => {
		e.preventDefault();
		e.stopPropagation();
	};

	/**
	 * Highlight drop zone
	 */
	const highlight = (): void => {
		dropZone.classList.add("border-primary", "bg-primary/10");
	};

	/**
	 * Remove highlight from drop zone
	 */
	const unhighlight = (): void => {
		dropZone.classList.remove("border-primary", "bg-primary/10");
	};

	// File input change handler
	fileInput.addEventListener("change", (e: Event) => {
		const target = e.target as HTMLInputElement;
		if (target.files?.[0]) {
			handleFileSelect(target.files[0]);
		}
	});

	// Drag and drop handlers
	["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
		dropZone.addEventListener(
			eventName,
			preventDefaults as EventListener,
			false,
		);
	});

	dropZone.addEventListener("dragenter", highlight);
	dropZone.addEventListener("dragover", highlight);
	dropZone.addEventListener("dragleave", unhighlight);

	dropZone.addEventListener("drop", (e: DragEvent) => {
		unhighlight();
		const dt = e.dataTransfer;
		if (dt?.files?.[0]) {
			handleFileSelect(dt.files[0]);
		}
	});

	// Click to upload (mobile-friendly)
	dropZone.addEventListener("click", () => {
		fileInput.click();
	});

	// Delete button handler
	if (deleteBtn) {
		deleteBtn.addEventListener("click", (e: Event) => {
			e.preventDefault();
			e.stopPropagation();
			if (deleteInput) {
				deleteInput.checked = true;
			}
			if (previewContainer) {
				previewContainer.classList.add("hidden");
			}
			if (existingImageContainer) {
				existingImageContainer.classList.add("hidden");
			}
			if (dropZone) {
				dropZone.classList.remove("hidden");
			}
			if (fileInput) {
				fileInput.value = "";
			}
		});
	}

	// Replace button handler
	if (replaceBtn) {
		replaceBtn.addEventListener("click", (e: Event) => {
			e.preventDefault();
			e.stopPropagation();
			fileInput.click();
		});
	}

	// Second set of buttons for preview container
	const replaceBtn2 = document.getElementById(
		"profile-image-replace-btn-2",
	) as HTMLButtonElement;
	const deleteBtn2 = document.getElementById(
		"profile-image-delete-btn-2",
	) as HTMLButtonElement;

	if (replaceBtn2) {
		replaceBtn2.addEventListener("click", (e: Event) => {
			e.preventDefault();
			e.stopPropagation();
			fileInput.click();
		});
	}

	if (deleteBtn2) {
		deleteBtn2.addEventListener("click", (e: Event) => {
			e.preventDefault();
			e.stopPropagation();
			if (deleteInput) {
				deleteInput.checked = true;
			}
			if (previewContainer) {
				previewContainer.classList.add("hidden");
			}
			if (existingImageContainer) {
				existingImageContainer.classList.add("hidden");
			}
			if (dropZone) {
				dropZone.classList.remove("hidden");
			}
			if (fileInput) {
				fileInput.value = "";
			}
		});
	}
});
