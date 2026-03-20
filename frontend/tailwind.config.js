/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Mission-console dark theme palette
        aegis: {
          bg: "#0a0e17",
          surface: "#111827",
          panel: "#1a2234",
          border: "#2a3548",
          accent: "#3b82f6",
          "accent-dim": "#1e3a5f",
          success: "#22c55e",
          warning: "#f59e0b",
          danger: "#ef4444",
          critical: "#dc2626",
          text: "#e2e8f0",
          "text-dim": "#94a3b8",
          "text-muted": "#64748b",
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', "monospace"],
        sans: ['"Inter"', "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        blink: "blink 1s step-end infinite",
      },
      keyframes: {
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
      },
    },
  },
  plugins: [],
};
