(() => {
  const dogSources = [
    'url("/static/local/dogs/dog-1.svg")',
    'url("/static/local/dogs/dog-2.svg")',
    'url("/static/local/dogs/dog-3.svg")',
    'url("/static/local/dogs/dog-4.svg")',
  ];

  const applyDog = (el, index) => {
    el.style.setProperty("--dog-src", dogSources[index]);
    el.dataset.dogIndex = String(index);
  };

  const readCycleMs = (el) => {
    const raw = getComputedStyle(el).getPropertyValue("--dog-cycle").trim();
    if (!raw) return 2600;
    if (raw.endsWith("ms")) return Number.parseFloat(raw);
    if (raw.endsWith("s")) return Number.parseFloat(raw) * 1000;
    return 2600;
  };

  const startCycle = (el) => {
    const duration = readCycleMs(el);
    if (!Number.isFinite(duration) || duration <= 0) return;
    const current = Number(el.dataset.dogIndex || 0);
    const next = (current + 1) % dogSources.length;
    el.dataset.dogIndex = String(current);
    el.dataset.dogTimer = String(
      window.setInterval(() => {
        const idx = Number(el.dataset.dogIndex || 0);
        const nextIndex = (idx + 1) % dogSources.length;
        applyDog(el, nextIndex);
      }, duration)
    );
    applyDog(el, next);
  };

  const stopCycle = (el) => {
    const timerId = Number(el.dataset.dogTimer);
    if (Number.isFinite(timerId)) {
      window.clearInterval(timerId);
    }
    delete el.dataset.dogTimer;
  };

  const bound = new WeakSet();

  const bindAll = () => {
    const runners = document.querySelectorAll(".logo-runner");
    runners.forEach((el, index) => {
      if (bound.has(el)) return;
      bound.add(el);
      applyDog(el, index % dogSources.length);
      el.addEventListener("mouseenter", () => startCycle(el));
      el.addEventListener("mouseleave", () => stopCycle(el));
    });
  };

  const observe = () => {
    const observer = new MutationObserver(() => bindAll());
    observer.observe(document.body, { childList: true, subtree: true });
  };

  const init = () => {
    bindAll();
    observe();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
