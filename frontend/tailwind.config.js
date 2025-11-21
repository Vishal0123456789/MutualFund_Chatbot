/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'soft-blue': '#f0f4f8',
        'soft-gray': '#f8f9fa',
        'accent-blue': '#5b8cde',
        'text-dark': '#2c3e50',
      }
    },
  },
  plugins: [],
}
