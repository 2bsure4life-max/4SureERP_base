document.addEventListener("DOMContentLoaded", function () {
  // Wait 1 second after load before hiding
  setTimeout(() => {
    const loading = document.getElementById("loading-screen");
    loading.style.opacity = "0";
    setTimeout(() => loading.remove(), 600); // Remove from DOM
  }, 1200);
});

