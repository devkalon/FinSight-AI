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
        background: '#080C14',
        surface: '#0E1422',
        'surface-elevated': '#151E33',
        'surface-hover': '#1A243D',
        border: '#1C2740',
        'border-focus': '#2E416B',
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          light: '#60A5FA',
          subtle: 'rgba(59, 130, 246, 0.12)',
        },
        emerald: {
          DEFAULT: '#10B981',
          500: '#10B981',
          400: '#34D399',
          subtle: 'rgba(16, 185, 129, 0.12)',
        },
        rose: {
          DEFAULT: '#F43F5E',
          500: '#F43F5E',
          400: '#FB7185',
          subtle: 'rgba(244, 63, 94, 0.12)',
        },
        amber: {
          DEFAULT: '#F59E0B',
          500: '#F59E0B',
          400: '#FBBF24',
          subtle: 'rgba(245, 158, 11, 0.12)',
        }
      },
    },
  },
  plugins: [],
}
