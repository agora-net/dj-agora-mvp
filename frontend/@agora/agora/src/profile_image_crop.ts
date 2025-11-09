/**
 * Profile Image Cropping Handler
 *
 * Uses cropperjs to allow users to crop their profile image before uploading.
 */

import Cropper from "cropperjs";

document.addEventListener("DOMContentLoaded", () => {
	const cropModal = document.getElementById(
		"profile-image-crop-modal",
	) as HTMLElement;
	const cropImage = document.getElementById(
		"profile-image-crop-img",
	) as HTMLImageElement;
	const cropCancelBtn = document.getElementById(
		"profile-image-crop-cancel",
	) as HTMLButtonElement;
	const cropConfirmBtn = document.getElementById(
		"profile-image-crop-confirm",
	) as HTMLButtonElement;
	const previewImage = document.getElementById(
		"profile-image-preview-img",
	) as HTMLImageElement;
	const fileInput = document.getElementById(
		"id_profile_image",
	) as HTMLInputElement;

	if (!cropModal || !cropImage || !previewImage) {
		return;
	}

	let cropper: Cropper | null = null;

	/**
	 * Initialize cropper when modal opens
	 */
	const initCropper = (imageSrc: string): void => {
		if (cropper) {
			cropper.destroy();
		}

		cropImage.src = imageSrc;
		cropper = new Cropper(cropImage, {
			aspectRatio: 1, // Square crop for profile images
			viewMode: 1, // Restrict crop box within canvas
			dragMode: "move",
			autoCropArea: 0.8,
			restore: false,
			guides: true,
			center: true,
			highlight: false,
			cropBoxMovable: true,
			cropBoxResizable: true,
			toggleDragModeOnDblclick: false,
		});
	};

	/**
	 * Show crop modal
	 */
	const showCropModal = (imageSrc: string): void => {
		if (cropModal) {
			cropModal.classList.remove("hidden");
			initCropper(imageSrc);
		}
	};

	/**
	 * Hide crop modal
	 */
	const hideCropModal = (): void => {
		if (cropModal) {
			cropModal.classList.add("hidden");
		}
		if (cropper) {
			cropper.destroy();
			cropper = null;
		}
	};

	/**
	 * Get cropped image as blob
	 */
	const getCroppedImage = (): Promise<Blob> => {
		return new Promise((resolve, reject) => {
			if (!cropper) {
				reject(new Error("Cropper not initialized"));
				return;
			}

			const canvas = cropper.getCroppedCanvas({
				width: 2048,
				height: 2048,
				imageSmoothingEnabled: true,
				imageSmoothingQuality: "high",
			});

			canvas.toBlob(
				(blob) => {
					if (blob) {
						resolve(blob);
					} else {
						reject(new Error("Failed to create blob"));
					}
				},
				"image/webp",
				0.95,
			);
		});
	};

	/**
	 * Handle crop confirmation
	 */
	const handleCropConfirm = async (): Promise<void> => {
		if (!cropper) {
			return;
		}

		try {
			const blob = await getCroppedImage();
			const file = new File([blob], "profile-image.webp", {
				type: "image/webp",
			});

			// Update file input
			if (fileInput) {
				const dataTransfer = new DataTransfer();
				dataTransfer.items.add(file);
				fileInput.files = dataTransfer.files;
			}

			// Update preview
			const previewContainer = document.getElementById(
				"profile-image-preview",
			) as HTMLElement;
			const existingImageContainer = document.getElementById(
				"profile-image-existing",
			) as HTMLElement;
			const deleteInput = document.getElementById(
				"delete_profile_image",
			) as HTMLInputElement;

			const reader = new FileReader();
			reader.onload = (e: ProgressEvent<FileReader>) => {
				if (e.target?.result) {
					previewImage.src = e.target.result as string;
					const dropZone = document.getElementById(
						"profile-image-dropzone",
					) as HTMLElement;

					if (previewContainer) {
						previewContainer.classList.remove("hidden");
					}
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
			};
			reader.readAsDataURL(blob);

			hideCropModal();
		} catch (error) {
			console.error("Error cropping image:", error);
			alert("Failed to crop image. Please try again.");
		}
	};

	// Cancel button handler
	if (cropCancelBtn) {
		cropCancelBtn.addEventListener("click", () => {
			hideCropModal();
		});
	}

	// Confirm button handler
	if (cropConfirmBtn) {
		cropConfirmBtn.addEventListener("click", () => {
			handleCropConfirm();
		});
	}

	// Close modal on backdrop click
	if (cropModal) {
		cropModal.addEventListener("click", (e: MouseEvent) => {
			if (e.target === cropModal) {
				hideCropModal();
			}
		});
	}

	// Expose function to show crop modal (called from upload handler)
	(window as any).showProfileImageCrop = (imageSrc: string) => {
		showCropModal(imageSrc);
	};
});
