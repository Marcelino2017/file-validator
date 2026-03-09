/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#edf6ff",
          100: "#d8ebff",
          500: "#245e8a",
          700: "#1b4b6f",
          900: "#132d43",
        },
        accent: "#2e8b57",
      },
      fontFamily: {
        sans: ["'Manrope'", "'Segoe UI'", "sans-serif"],
      },
      boxShadow: {
        card: "0 10px 30px rgba(19, 45, 67, 0.12)",
      },
    },
  },
  plugins: [],
};
