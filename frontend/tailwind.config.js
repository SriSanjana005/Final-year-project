/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: "#2563EB",
          dark: "#0F172A",
          bg: "#F8FAFC",
          card: "#FFFFFF",
          success: "#14B8A6",
          warning: "#F59E0B",
          error: "#EF4444",
        }
      }
    },
  },
  plugins: [],
}
