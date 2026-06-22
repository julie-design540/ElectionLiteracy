document.addEventListener("DOMContentLoaded", () => {
  const loader = document.getElementById("page-loader");
  if (loader) {
    window.setTimeout(() => loader.classList.add("is-hidden"), 180);
  }

  const themeToggle = document.getElementById("themeToggle");
  const root = document.documentElement;
  const storedTheme = window.localStorage.getItem("theme") || "light";
  const themeIcon = themeToggle ? themeToggle.querySelector("i") : null;
  root.setAttribute("data-theme", storedTheme);
  if (themeIcon) {
    themeIcon.className = storedTheme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars";
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", nextTheme);
      window.localStorage.setItem("theme", nextTheme);
      if (themeIcon) {
        themeIcon.className = nextTheme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars";
      }
    });
  }

  const counters = document.querySelectorAll("[data-count]");
  const animateCounter = (element) => {
    const target = Number(element.dataset.count || 0);
    const duration = 900;
    const start = performance.now();
    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      element.textContent = Math.floor(progress * target).toLocaleString();
      if (progress < 1) {
        window.requestAnimationFrame(tick);
      } else {
        element.textContent = target.toLocaleString();
      }
    };
    window.requestAnimationFrame(tick);
  };

  if (counters.length) {
    counters.forEach((counter) => animateCounter(counter));
  }

  const toastEls = document.querySelectorAll(".toast");
  if (toastEls.length) {
    toastEls.forEach((toast) => {
      window.setTimeout(() => toast.classList.remove("show"), 4500);
    });
  }

  const revealTargets = document.querySelectorAll(".reveal-card, .glass-card, .art-card, .mini-activity, .queue-card");
  if ("IntersectionObserver" in window && revealTargets.length) {
    revealTargets.forEach((element) => element.classList.add("reveal-ready"));
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealTargets.forEach((element) => observer.observe(element));
  }

  const chartElement = document.getElementById("statusChart");
  if (chartElement && window.Chart) {
    const labels = JSON.parse(chartElement.dataset.labels || "[]");
    const values = JSON.parse(chartElement.dataset.values || "[]");
    new Chart(chartElement, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Artwork count",
            data: values,
            backgroundColor: ["#f5b700", "#1b5e20", "#b41f26"],
            borderColor: ["#d99f00", "#12451a", "#8f151b"],
            borderWidth: 0,
            borderRadius: 12,
            maxBarThickness: 62,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            top: 8,
            right: 8,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              color: "#475569",
              font: {
                weight: 700,
              },
            },
          },
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(15, 23, 42, 0.08)",
            },
            border: {
              display: false,
            },
            ticks: {
              precision: 0,
              color: "#64748b",
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "#0b0b0b",
            borderColor: "rgba(245, 183, 0, 0.45)",
            borderWidth: 1,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: (context) => `${context.parsed.y.toLocaleString()} artworks`,
            },
          },
        },
      },
    });
  }

  const categoryChartElement = document.getElementById("categoryChart");
  if (categoryChartElement && window.Chart) {
    const labels = JSON.parse(categoryChartElement.dataset.labels || "[]");
    const values = JSON.parse(categoryChartElement.dataset.values || "[]");
    new Chart(categoryChartElement, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Submissions",
            data: values,
            backgroundColor: "rgba(27, 94, 32, 0.86)",
            hoverBackgroundColor: "#b41f26",
            borderRadius: 10,
            maxBarThickness: 28,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            beginAtZero: true,
            grid: {
              color: "rgba(15, 23, 42, 0.08)",
            },
            border: {
              display: false,
            },
            ticks: {
              precision: 0,
              color: "#64748b",
            },
          },
          y: {
            grid: {
              display: false,
            },
            ticks: {
              color: "#334155",
              font: {
                weight: 700,
              },
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "#0b0b0b",
            borderColor: "rgba(27, 94, 32, 0.35)",
            borderWidth: 1,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: (context) => `${context.parsed.x.toLocaleString()} submissions`,
            },
          },
        },
      },
    });
  }

  const artworkInput = document.getElementById("artwork-image-input");
  const artworkDropzone = document.getElementById("artworkDropzone");
  const artworkPreviewImage = document.getElementById("artworkPreviewImage");
  const artworkPreview = document.getElementById("artworkPreview");
  const artworkFileName = document.getElementById("artworkFileName");

  const renderArtworkPreview = (file) => {
    if (!file || !artworkPreviewImage || !artworkPreview || !artworkFileName) {
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      artworkPreviewImage.src = String(event.target?.result || "");
      artworkPreviewImage.classList.remove("d-none");
      artworkPreview.classList.add("d-none");
      artworkFileName.textContent = file.name;
    };
    reader.readAsDataURL(file);
  };

  if (artworkInput) {
    artworkInput.addEventListener("change", () => {
      const [file] = artworkInput.files || [];
      renderArtworkPreview(file);
    });
  }

  if (artworkDropzone) {
    artworkDropzone.addEventListener("dragover", (event) => {
      event.preventDefault();
      artworkDropzone.classList.add("is-dragover");
    });
    artworkDropzone.addEventListener("dragleave", () => {
      artworkDropzone.classList.remove("is-dragover");
    });
    artworkDropzone.addEventListener("drop", (event) => {
      event.preventDefault();
      artworkDropzone.classList.remove("is-dragover");
      if (artworkInput && event.dataTransfer?.files?.length) {
        const transfer = new DataTransfer();
        transfer.items.add(event.dataTransfer.files[0]);
        artworkInput.files = transfer.files;
        renderArtworkPreview(event.dataTransfer.files[0]);
      }
    });
  }

  const lessonPages = Array.from(document.querySelectorAll("[data-lesson-page]"));
  const lessonCurrent = document.getElementById("lessonPageCurrent");
  const lessonTotal = document.getElementById("lessonPageTotal");
  const lessonPrev = document.getElementById("lessonPrevPage");
  const lessonNext = document.getElementById("lessonNextPage");
  const lessonReachedEnd = document.getElementById("lessonReachedEnd");
  const lessonCompleteButton = document.getElementById("lessonCompleteButton");
  let lessonPageIndex = 0;

  const renderLessonPage = () => {
    if (!lessonPages.length) {
      return;
    }
    lessonPages.forEach((page, index) => {
      page.classList.toggle("d-none", index !== lessonPageIndex);
    });
    if (lessonCurrent) {
      lessonCurrent.textContent = String(lessonPageIndex + 1);
    }
    if (lessonTotal) {
      lessonTotal.textContent = String(lessonPages.length);
    }
    if (lessonPrev) {
      lessonPrev.disabled = lessonPageIndex === 0;
    }
    if (lessonNext) {
      lessonNext.innerHTML =
        lessonPageIndex === lessonPages.length - 1 ? 'Finish reading <i class="bi bi-check2"></i>' : 'Next <i class="bi bi-arrow-right"></i>';
    }
  };

  if (lessonPages.length) {
    renderLessonPage();
  }

  if (lessonPrev) {
    lessonPrev.addEventListener("click", () => {
      lessonPageIndex = Math.max(lessonPageIndex - 1, 0);
      renderLessonPage();
    });
  }

  if (lessonNext) {
    lessonNext.addEventListener("click", () => {
      if (lessonPageIndex < lessonPages.length - 1) {
        lessonPageIndex += 1;
        renderLessonPage();
        return;
      }
      if (lessonReachedEnd) {
        lessonReachedEnd.value = "1";
      }
      if (lessonCompleteButton) {
        lessonCompleteButton.disabled = false;
        lessonCompleteButton.classList.add("is-unlocked");
        lessonCompleteButton.focus();
      }
    });
  }
});
