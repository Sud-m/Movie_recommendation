/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        netflix: {
          red: '#9333EA', // Purple primary
          'red-dark': '#7C3AED', // Purple dark (darker shade)
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

