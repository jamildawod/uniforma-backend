import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#131A22",
        sand: "#F5F1E8",
        clay: "#C76B47",
        moss: "#5B6B4A",
        steel: "#4B5D73"
      },
      boxShadow: {
        panel: "0 14px 36px rgba(19, 26, 34, 0.08)"
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};

export default config;
