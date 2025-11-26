/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        netflix: {
          red: '#D4A017', // Cinematic Gold
          'red-dark': '#8C6A12', // Deep Gold (darker shade)
          black: '#141414',
          'gray-dark': '#181818',
          'gray-medium': '#2F2F2F',
        }
      },
      fontFamily: {
        netflix: ['Netflix Sans', 'Helvetica Neue', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

