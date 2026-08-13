Here's a clean approach using CSS variables, a small hook, and no extra dependencies.

## 1. Define theme variables in CSS

```css
/* index.css */
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
  --accent: #3b82f6;
  --border: #e5e7eb;
}

[data-theme="dark"] {
  --bg: #121212;
  --text: #f0f0f0;
  --accent: #60a5fa;
  --border: #2d2d2d;
}

body {
  background: var(--bg);
  color: var(--text);
  transition: background 0.2s ease, color 0.2s ease;
}
```

Use `data-theme` on `<html>` (or `<body>`) rather than a class — it reads clearly and avoids specificity fights.

## 2. Resolve the initial theme before paint

To avoid a flash of the wrong theme, set the attribute as early as possible — ideally inline in `index.html`, before React even mounts:

```html
<!-- index.html, in <head> -->
<script>
  (function () {
    const stored = localStorage.getItem('theme');
    const theme = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

This runs synchronously before render, so there's no flicker — React doesn't need to "catch up" after mount.

## 3. A small hook to manage/toggle theme in React

```jsx
// useTheme.js
import { useState, useEffect, useCallback } from 'react';

function getInitialTheme() {
  return document.documentElement.getAttribute('data-theme') || 'light';
}

export function useTheme() {
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'));
  }, []);

  return [theme, toggleTheme];
}
```

Reading the initial state from the DOM attribute (already set by the inline script) keeps React in sync with what's already on screen instead of redoing the media-query logic.

## 4. Toggle button

```jsx
// ThemeToggle.jsx
import { useTheme } from './useTheme';

export function ThemeToggle() {
  const [theme, toggleTheme] = useTheme();
  return (
    <button onClick={toggleTheme} aria-label="Toggle dark mode">
      {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
}
```

## 5. Optional: respond to OS changes when no explicit choice was made

If you want the app to keep following the OS setting until the user manually picks a theme:

```js
useEffect(() => {
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const handler = (e) => {
    if (!localStorage.getItem('theme')) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  };
  mq.addEventListener('change', handler);
  return () => mq.removeEventListener('change', handler);
}, []);
```

### Why this structure
- **Inline script in `index.html`** avoids the flash-of-wrong-theme problem that a `useEffect`-only approach can't fully solve.
- **CSS variables + `data-theme` attribute** keep all color logic in CSS, so components stay theme-agnostic.
- **`localStorage.getItem('theme')` as the source of truth** for "did the user explicitly choose?" lets you distinguish an explicit choice from just following the OS.
