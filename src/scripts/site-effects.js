import AOS from 'aos';
import confetti from 'canvas-confetti';
import { fairyDustCursor } from 'cursor-effects';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const finePointer = window.matchMedia('(pointer: fine)');

function enhanceCards() {
  const targets = document.querySelectorAll(
    '.cn-card, .resource-card, .notice-box, .sl-markdown-content > table, .sl-markdown-content > blockquote'
  );

  targets.forEach((target, index) => {
    if (target.dataset.aos) return;
    target.dataset.aos = 'fade';
    target.dataset.aosDuration = '560';
    target.dataset.aosEasing = 'ease-out-cubic';
    target.dataset.aosDelay = String(Math.min((index % 6) * 35, 175));
    target.dataset.aosAnchorPlacement = 'top-bottom';
  });
}

function enhancePointerGlow() {
  const glow = document.createElement('div');
  glow.className = 'cn-pointer-glow';
  document.body.appendChild(glow);

  let nextX = 0;
  let nextY = 0;
  let currentX = 0;
  let currentY = 0;
  let frame = 0;
  let initialized = false;

  window.addEventListener(
    'pointermove',
    (event) => {
      nextX = event.clientX;
      nextY = event.clientY;
      if (!initialized) {
        currentX = nextX;
        currentY = nextY;
        initialized = true;
      }
      glow.dataset.active = 'true';
    },
    { passive: true }
  );

  window.addEventListener('pointerleave', () => {
    glow.dataset.active = 'false';
  });

  document.querySelectorAll('.pdf-preview').forEach((preview) => {
    preview.addEventListener('pointerenter', () => {
      glow.dataset.active = 'false';
    });
    preview.addEventListener('mouseenter', () => {
      glow.dataset.active = 'false';
    });
  });

  const render = () => {
    currentX += (nextX - currentX) * 0.3;
    currentY += (nextY - currentY) * 0.3;
    glow.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
    frame = window.requestAnimationFrame(render);
  };

  render();
  return () => {
    window.cancelAnimationFrame(frame);
    glow.remove();
  };
}

function enhanceCursorDot() {
  const dot = document.createElement('div');
  dot.className = 'cn-cursor-dot';
  document.body.appendChild(dot);

  let nextX = 0;
  let nextY = 0;
  let currentX = 0;
  let currentY = 0;
  let initialized = false;
  let frame = 0;

  window.addEventListener(
    'pointermove',
    (event) => {
      nextX = event.clientX;
      nextY = event.clientY;
      if (!initialized) {
        currentX = nextX;
        currentY = nextY;
        initialized = true;
      }
      dot.dataset.active = 'true';
    },
    { passive: true }
  );

  window.addEventListener('pointerdown', () => {
    dot.dataset.press = 'true';
  });

  window.addEventListener('pointerup', () => {
    dot.dataset.press = 'false';
  });

  window.addEventListener('pointerleave', () => {
    dot.dataset.active = 'false';
  });

  document.querySelectorAll('.pdf-preview').forEach((preview) => {
    const hideDot = () => {
      dot.dataset.active = 'false';
      dot.dataset.press = 'false';
    };
    preview.addEventListener('pointerenter', hideDot);
    preview.addEventListener('mouseenter', hideDot);
  });

  const render = () => {
    currentX += (nextX - currentX) * 0.46;
    currentY += (nextY - currentY) * 0.46;
    dot.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
    frame = window.requestAnimationFrame(render);
  };

  render();
  return () => {
    window.cancelAnimationFrame(frame);
    dot.remove();
  };
}

function enhanceClickBurst() {
  const burst = (point, intensity = 1) => {
    const isLight = document.documentElement.dataset.theme === 'light';
    const colors = isLight ? ['#083b86', '#007d76', '#b37b00'] : ['#12d5cc', '#6ee7ff', '#f4c542'];
    const origin = {
      x: point.clientX / window.innerWidth,
      y: point.clientY / window.innerHeight,
    };

    confetti({
      particleCount: Math.round(28 * intensity),
      spread: 46,
      startVelocity: 24,
      scalar: 0.66,
      ticks: 88,
      gravity: 1.0,
      origin,
      colors,
      disableForReducedMotion: true,
    });
    window.setTimeout(() => {
      confetti({
        particleCount: Math.round(12 * intensity),
        spread: 74,
        startVelocity: 16,
        scalar: 0.46,
        ticks: 70,
        gravity: 0.95,
        origin,
        colors,
        disableForReducedMotion: true,
      });
    }, 80);
  };

  document.addEventListener('click', (event) => {
    const link = event.target instanceof Element ? event.target.closest('a') : null;
    if (!link || event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (link.target && link.target !== '_self') return;

    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin) return;
    if (url.pathname === window.location.pathname && url.hash) return;

    try {
      sessionStorage.setItem(
        'cn-click-burst',
        JSON.stringify({
          x: event.clientX,
          y: event.clientY,
          at: Date.now(),
        })
      );
    } catch {
      // Ignore storage failures; the local burst still runs.
    }
    burst(event, 1.25);
  });

  window.addEventListener(
    'pointerdown',
    (event) => {
      if (event.button !== 0) return;
      if (event.target instanceof Element && event.target.closest('a')) return;
      burst(event, 1);
    },
    { passive: true }
  );

  try {
    const stored = sessionStorage.getItem('cn-click-burst');
    if (!stored) return;
    sessionStorage.removeItem('cn-click-burst');
    const data = JSON.parse(stored);
    if (!data || Date.now() - data.at > 1800) return;
    window.setTimeout(() => {
      burst({ clientX: data.x, clientY: data.y }, 0.95);
    }, 80);
  } catch {
    // Ignore malformed stored animation state.
  }
}

function liftCursorCanvases() {
  document.querySelectorAll('body > canvas').forEach((canvas) => {
    canvas.style.zIndex = '2147483641';
    canvas.classList.add('cn-cursor-canvas');
  });
}

function init() {
  if (reduceMotion.matches) return;

  enhanceCards();
  AOS.init({
    once: true,
    offset: 48,
    duration: 560,
    easing: 'ease-out-cubic',
    disableMutationObserver: false,
  });

  if (finePointer.matches) {
    fairyDustCursor({
      colors: ['#083b86', '#00a99d', '#f4c542'],
    });
    liftCursorCanvases();
    window.setTimeout(liftCursorCanvases, 200);
    enhancePointerGlow();
    enhanceCursorDot();
    enhanceClickBurst();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init, { once: true });
} else {
  init();
}
