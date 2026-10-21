/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ghana: {
          red: '#CE1126',
          gold: '#FCD116',
          green: '#006B3F',
          black: '#000000',
        },
        momo: {
          yellow: '#FFCC00',
          dark: '#231F20',
        },
        telecel: {
          red: '#E60000',
        },
        at: {
          blue: '#002B49',
          orange: '#FF671B',
        }
      }
    },
  },
  plugins: [],
}
