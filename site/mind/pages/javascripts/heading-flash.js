(() => {
  const FLASH_CLASS = "mind-heading-flash";
  const FLASH_MS = 1900;

  function flashHeadingFromHash(hash) {
    if (!hash || hash === "#") {
      return;
    }

    const id = decodeURIComponent(hash.slice(1));
    if (!id) {
      return;
    }

    const heading = document.querySelector(
      `.md-typeset :is(h2, h3, h4, h5, h6)[id="${CSS.escape(id)}"]`
    );
    if (!heading) {
      return;
    }

    heading.classList.remove(FLASH_CLASS);
    void heading.offsetWidth;
    heading.classList.add(FLASH_CLASS);

    window.setTimeout(() => {
      heading.classList.remove(FLASH_CLASS);
    }, FLASH_MS);
  }

  function handleAnchorClick(event) {
    const link = event.target instanceof Element
      ? event.target.closest('a[href^="#"], a[href*="#"]')
      : null;

    if (!link) {
      return;
    }

    const href = link.getAttribute("href") || "";
    const hashIndex = href.indexOf("#");
    if (hashIndex < 0) {
      return;
    }

    const hash = href.slice(hashIndex);
    if (!hash) {
      return;
    }

    window.setTimeout(() => {
      flashHeadingFromHash(hash);
    }, 80);
  }

  document.addEventListener("click", handleAnchorClick, true);
  window.addEventListener("hashchange", () => flashHeadingFromHash(window.location.hash));
  window.addEventListener("load", () => flashHeadingFromHash(window.location.hash));
})();
