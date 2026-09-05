/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        fintech: {
          bg: '#080C14',
          card: '#0D1322',
          cardHover: '#121B2F',
          border: '#1A263D',
          borderSubtle: '#141D30',
          subtle: '#080D18',
          positive: '#10B981',
          negative: '#F43F5E',
          benchmark: '#3B82F6',
          cyan: '#06B6D4',
          amber: '#F59E0B',
          purple: '#8B5CF6',
          textHeading: '#FFFFFF',
          textBody: '#E2E8F0',
          textMuted: '#94A3B8',
          textDim: '#64748B'
        }
      },
      boxShadow: {
        'fintech-card': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.06), 0 4px 20px -2px rgba(0, 0, 0, 0.5)',
        'fintech-hover': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 8px 30px -4px rgba(59, 130, 246, 0.15)',
        'glow-cyan': '0 0 20px -4px rgba(6, 182, 212, 0.3)',
        'glow-emerald': '0 0 20px -4px rgba(16, 185, 129, 0.3)',
        'glow-blue': '0 0 20px -4px rgba(59, 130, 246, 0.3)',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
      }
    },
  },
  plugins: [],
}
