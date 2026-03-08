// DOM Elements
const imageInput = document.getElementById("imageInput");
const detectBtn = document.getElementById("detectBtn");
const resetBtn = document.getElementById("resetBtn");
const resultsSection = document.getElementById("resultsSection");
const loadingSpinner = document.getElementById("loadingSpinner");
const errorMessage = document.getElementById("errorMessage");
const originalImage = document.getElementById("originalImage");
const resultImage = document.getElementById("resultImage");
const detectionsList = document.getElementById("detectionsList");
const confidenceSlider = document.getElementById("confidenceSlider");
const confidenceValue = document.getElementById("confidenceValue");
const uploadLabel = document.querySelector(".upload-label");

// Prevent default drag behaviors
["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  uploadLabel.addEventListener(eventName, preventDefaults, false);
  document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

// Highlight drop area when dragging files
["dragenter", "dragover"].forEach((eventName) => {
  uploadLabel.addEventListener(eventName, () => {
    uploadLabel.style.borderColor = "#764ba2";
    uploadLabel.style.background = "#f3e5f5";
  });
});

["dragleave", "drop"].forEach((eventName) => {
  uploadLabel.addEventListener(eventName, () => {
    uploadLabel.style.borderColor = "#0066cc";
    uploadLabel.style.background = "#f5f7fa";
  });
});

// Handle dropped files
uploadLabel.addEventListener("drop", async (e) => {
  const dt = e.dataTransfer;
  const files = dt.files;
  imageInput.files = files;
  handleFileSelect();
});

// Handle file input change
imageInput.addEventListener("change", handleFileSelect);

function handleFileSelect() {
  const file = imageInput.files[0];

  if (!file) {
    detectBtn.disabled = true;
    return;
  }

  // Validate file type
  const validTypes = ["image/jpeg", "image/png", "image/bmp", "image/gif"];
  if (!validTypes.includes(file.type)) {
    showError(
      "Invalid file type. Please upload an image (JPG, PNG, BMP, or GIF)",
    );
    imageInput.value = "";
    detectBtn.disabled = true;
    return;
  }

  // Validate file size (50MB)
  if (file.size > 50 * 1024 * 1024) {
    showError("File is too large. Maximum size is 50MB");
    imageInput.value = "";
    detectBtn.disabled = true;
    return;
  }

  detectBtn.disabled = false;
  hideError();
  resultsSection.style.display = "none";
}

// Confidence slider
confidenceSlider.addEventListener("input", (e) => {
  const value = e.target.value;
  confidenceValue.textContent = value + "%";
});

// Detect button click
detectBtn.addEventListener("click", detectFish);

async function detectFish() {
  const file = imageInput.files[0];
  if (!file) {
    showError("Please select an image first");
    return;
  }

  const confidence = confidenceSlider.value / 100;

  // Create FormData
  const formData = new FormData();
  formData.append("file", file);
  formData.append("confidence", confidence);

  // Show loading state
  showLoading();
  hideError();

  try {
    const response = await fetch("/api/detect", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || "An error occurred during detection");
      hideLoading();
      return;
    }

    // Display results
    displayResults(data);
    hideLoading();
  } catch (error) {
    console.error("Error:", error);
    showError("Network error. Please try again.");
    hideLoading();
  }
}

function displayResults(data) {
  // Display images
  originalImage.src = data.original_image_url + "?t=" + Date.now();
  resultImage.src = data.result_image_url + "?t=" + Date.now();

  // Display detections
  detectionsList.innerHTML = "";

  if (data.detections_count === 0) {
    detectionsList.innerHTML =
      '<p style="color: #666; padding: 20px; text-align: center;">No fish detected in this image. Try adjusting the confidence threshold.</p>';
  } else {
    data.detections.forEach((detection) => {
      const div = document.createElement("div");
      div.className = "detection-item";
      div.innerHTML = `
                <strong>Fish ${detection.id}</strong>
                <span class="detection-confidence">${detection.confidence}</span>
            `;
      detectionsList.appendChild(div);
    });

    // Summary
    const summary = document.createElement("div");
    summary.style.marginTop = "15px";
    summary.style.paddingTop = "15px";
    summary.style.borderTop = "2px solid #ddd";
    summary.innerHTML = `<strong>Total Detections: ${data.detections_count}</strong>`;
    detectionsList.appendChild(summary);
  }

  // Show results section
  resultsSection.style.display = "block";
  resultsSection.scrollIntoView({ behavior: "smooth" });
}

// Reset button
resetBtn.addEventListener("click", () => {
  imageInput.value = "";
  resultsSection.style.display = "none";
  detectBtn.disabled = true;
  hideError();
  confidenceSlider.value = 50;
  confidenceValue.textContent = "50%";
});

function showLoading() {
  loadingSpinner.style.display = "block";
  detectBtn.disabled = true;
}

function hideLoading() {
  loadingSpinner.style.display = "none";
  if (imageInput.files.length > 0) {
    detectBtn.disabled = false;
  }
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
}

function hideError() {
  errorMessage.style.display = "none";
}

// Check API health on page load
async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    console.log("API Health:", data);
  } catch (error) {
    console.error("API Health Check Failed:", error);
  }
}

// Check health when page loads
window.addEventListener("load", checkHealth);
