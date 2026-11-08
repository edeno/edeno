// Autoplay is an HTML attribute, so prefers-reduced-motion can't disable it from CSS.
if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.addEventListener("DOMContentLoaded", () => {
    for (const video of document.querySelectorAll("video[autoplay]")) {
      video.removeAttribute("autoplay");
      video.pause();
    }
  });
}
