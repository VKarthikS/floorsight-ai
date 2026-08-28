const form = document.querySelector("[data-visualizer-form]");
const upload = document.querySelector("[data-room-upload]");
const preview = document.querySelector("[data-upload-preview]");
const previewImage = document.querySelector("[data-upload-preview-image]");
const clearUpload = document.querySelector("[data-clear-upload]");

function clearPreview() {
  if (upload) upload.value = "";
  if (previewImage?.src) URL.revokeObjectURL(previewImage.src);
  if (previewImage) previewImage.removeAttribute("src");
  if (preview) preview.hidden = true;
}

upload?.addEventListener("change", () => {
  const file = upload.files?.[0];
  if (!file || !preview || !previewImage) return clearPreview();
  previewImage.src = URL.createObjectURL(file);
  preview.hidden = false;
});

clearUpload?.addEventListener("click", clearPreview);

form?.addEventListener("submit", () => {
  const button = form.querySelector("[data-submit]");
  const label = form.querySelector("[data-submit-label]");
  const note = form.querySelector("[data-processing-note]");
  if (button) button.disabled = true;
  if (label) label.textContent = "Creating preview...";
  if (note) note.hidden = false;
});
