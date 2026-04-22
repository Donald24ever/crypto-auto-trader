import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0d10",
        panel: "#13171c",
        border: "#1f252d",
        brand: "#22c55e",
        danger: "#ef4444",
      },
    },
  },
  plugins: [],
};

export default config;
