/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          900: '#0f172a',
          950: '#020617',
        },
      },
      fontFamily: {
        display: ['"Bebas Neue"', 'sans-serif'],
        mono: ['"DM Mono"', '"Fira Code"', 'monospace'],
        serif: ['Fraunces', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}
