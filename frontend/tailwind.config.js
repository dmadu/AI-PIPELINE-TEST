/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#1976d2',
          dark: '#115293',
          light: '#4791db',
        },
      },
    },
  },
  plugins: [],
};
