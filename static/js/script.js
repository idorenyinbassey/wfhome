// Function to display the current time in the header
function showCurrentTime() {
    const timeElement = document.getElementById('current-time');
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    timeElement.textContent = `${hours}:${minutes}:${seconds}`;
}

// Function to set the current year in the footer
function updateYear() {
    const yearElement = document.getElementById('current-year');
    const currentYear = new Date().getFullYear();
    yearElement.textContent = currentYear;
}

// Call the functions when the page loads
window.onload = function () {
    showCurrentTime();
    setInterval(showCurrentTime, 1000);  // Update time every second
    updateYear();
}