document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.querySelector(".theme-toggle");
  const body = document.body;
  const crow = document.querySelector(".crow-mascot");

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    body.classList.remove("light", "dark");
    body.classList.add(savedTheme);
  } else {
    body.classList.add("dark");
  }

  toggleBtn.addEventListener("click", function () {
    if (body.classList.contains("dark")) {
      body.classList.replace("dark", "light");
      localStorage.setItem("theme", "light");
      if (crow) {
        crow.classList.add("wave");
        setTimeout(() => crow.classList.remove("wave"), 1500);
      }
    } else {
      body.classList.replace("light", "dark");
      localStorage.setItem("theme", "dark");
      if (crow) {
        crow.classList.add("swing");
        setTimeout(() => crow.classList.remove("swing"), 1500);
      }
    }
  });
});
