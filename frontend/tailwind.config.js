/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#1a1a1a",
          panel: "#2a2a2a",
          card: "#3a3a3a",
          input: "#4a4a4a",
          buy: "#00ff00",
          hold: "#ffff00",
          stop: "#ff0000",
          accent: "#00bfff",
          muted: "#888888",
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"IBM Plex Sans"', "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
