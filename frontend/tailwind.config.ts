import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        slateDeep: "#18324b",
        tide: "#0d4f57",
        sand: "#f5efe5",
        cream: "#fbfaf6",
        ember: "#b45309",
        alert: "#9f1239"
      },
      boxShadow: {
        panel: "0 18px 40px rgba(24, 50, 75, 0.12)"
      },
      backgroundImage: {
        "hero-grid":
          "radial-gradient(circle at top right, rgba(13,79,87,0.18), transparent 35%), radial-gradient(circle at 15% 20%, rgba(180,83,9,0.14), transparent 25%)"
      }
    }
  },
  plugins: []
};

export default config;
