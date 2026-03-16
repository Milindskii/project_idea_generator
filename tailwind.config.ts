import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class", // opt-in only; nothing auto-switches
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ["var(--font-playfair)", "serif"],
        sans: ["var(--font-dm-sans)", "sans-serif"],
      },
      colors: {
        primary: "#1A1A2E",
        accent: "#E8651A",
        paper: "#F5F0E8",
        success: "#2D6A4F",
      },
    },
  },
  plugins: [],
};
export default config;
