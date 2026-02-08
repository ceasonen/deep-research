/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        ink: '#102a43',
        mint: '#5bd1b6',
        ember: '#ff7d57',
        sand: '#f3efe6',
      },
      boxShadow: {
        soft: '0 12px 30px rgba(16, 42, 67, 0.12)',
      },
    },
  },
  plugins: [],
};
