/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{ts,tsx}',
    './src/components/**/*.{ts,tsx}',
    './src/app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090D16',
        surface: '#111827',
        'surface-elevated': '#1F2937',
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          light: '#60A5FA',
        },
        emerald: {
          500: '#10B981',
          400: '#34D399',
        },
        rose: {
          500: '#F43F5E',
          400: '#FB7185',
        },
        amber: {
          500: '#F59E0B',
          400: '#FBBF24',
        }
      },
    },
  },
  plugins: [],
}
