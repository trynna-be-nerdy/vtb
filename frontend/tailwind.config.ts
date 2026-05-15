import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        vtb: {
          primary: '#378add',
          'primary-content': '#ffffff',
          secondary: '#1d9e75',
          'secondary-content': '#ffffff',
          accent: '#7f77dd',
          'accent-content': '#ffffff',
          neutral: '#18181b',
          'neutral-content': '#f5f5f7',
          'base-100': '#ffffff',
          'base-200': '#f7f7f8',
          'base-300': '#f1f1f3',
          'base-content': '#18181b',
          info: '#378add',
          'info-content': '#ffffff',
          success: '#1d9e75',
          'success-content': '#ffffff',
          warning: '#e8a000',
          'warning-content': '#422006',
          error: '#dc2626',
          'error-content': '#ffffff',
          '--rounded-btn': '0.375rem',
          '--rounded-badge': '1.9rem',
          '--rounded-box': '0.75rem',
        },
      },
    ],
    darkTheme: false,
    base: true,
    styled: true,
    utils: true,
    logs: false,
  } as Record<string, unknown>,
}

export default config
