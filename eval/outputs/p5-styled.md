Add 4 pieces: CSS variables, an inline no-flash script, a theme hook, and a toggle button.

## Step 1: CSS variables (`src/index.css`)

```css
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
  --accent: #3366ff;
}

[data-theme="dark"] {
  --bg: #1a1a1a;
  --text: #f0f0f0;
  --accent: #6699ff;
}

body {
  background: var(--bg);
  color: var(--text);
}
```

`data-theme` is an attribute on `<html>`. It switches which variable set applies.

## Step 2: Set theme before React loads (avoids a flash of the wrong color)

Add this inline script in `index.html`, inside `<head>`, before your `<script type="module" src="/src/main.tsx">` tag:

```html
<script>
  (function () {
    var saved = localStorage.getItem('theme');
    var theme = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

This runs first. It checks `localStorage`. If nothing is saved, it checks the OS setting. Without this step, the page paints light, then flips to dark — a visible flash.

## Step 3: React hook (`src/useTheme.ts`)

```ts
import { useState, useEffect } from 'react';

export function useTheme() {
  const [theme, setTheme] = useState(
    () => document.documentElement.getAttribute('data-theme') || 'light'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  return { theme, toggleTheme };
}
```

The hook reads the attribute the Step 2 script already set. It does not repeat the OS check.

## Step 4: Toggle button

```tsx
import { useTheme } from './useTheme';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
}
```

Drop `<ThemeToggle />` anywhere in your app.

Result: colors switch through CSS variables, the choice persists in `localStorage`, and first-time visitors get their OS preference with no flash.

Next action: paste the Step 2 script into `index.html` first — the other three steps depend on `data-theme` already being set.
