import type { Config } from "tailwindcss";
import { heroui } from "@heroui/react";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["Georgia", "Times New Roman", "serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        navy: {
          900: "#0a0f1e",
          800: "#111827",
          700: "#1e2a3a",
        },
      },
    },
  },
  darkMode: "class",
  plugins: [
    heroui({
      defaultTheme: "dark",
      themes: {
        dark: {
          colors: {
            background: "#0a0f1e",
            foreground: "#e2e8f0",
            primary: { DEFAULT: "#3b82f6", foreground: "#ffffff" },
            secondary: { DEFAULT: "#8b5cf6", foreground: "#ffffff" },
          },
        },
      },
    }),
  ],
};

export default config;
