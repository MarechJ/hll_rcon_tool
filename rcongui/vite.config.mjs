import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import fs from "fs/promises";
import path from "path";

const DEFAULT_CRCON_SERVER_URL = "http://localhost:8010";
const DEFAULT_CRCON_API_ENDPOINT = "api";

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  if (mode === "production" && !env.REACT_APP_API_URL) {
    console.error("Error: REACT_APP_API_URL is not set in production mode");
    process.exit(1);
  }

  const REACT_APP_API_URL = env.REACT_APP_API_URL;
  const VITE_CRCON_SERVER_URL =
    env.VITE_CRCON_SERVER_URL ?? DEFAULT_CRCON_SERVER_URL;
  const VITE_CRCON_API_ENDPOINT =
    env.VITE_CRCON_API_ENDPOINT ?? DEFAULT_CRCON_API_ENDPOINT;
  const DEBUG = env.DEBUG;

  if (mode === "development") {
    if (!env.VITE_CRCON_SERVER_URL) {
      console.warn(
        "[dev] Warning: VITE_CRCON_SERVER_URL is not set - defaulting to '" +
          DEFAULT_CRCON_SERVER_URL +
          "'"
      );
    }

    if (!env.VITE_CRCON_API_ENDPOINT) {
      console.warn(
        "[dev] Warning: VITE_CRCON_API_ENDPOINT is not set - defaulting to '" +
          DEFAULT_CRCON_API_ENDPOINT +
          "'"
      );
    }
  }

  console.log(
    "[dev] Requests to",
    REACT_APP_API_URL,
    "will be proxied to",
    VITE_CRCON_SERVER_URL + VITE_CRCON_API_ENDPOINT
  );
  console.log(
    "[dev] API Documentation:",
    VITE_CRCON_SERVER_URL + VITE_CRCON_API_ENDPOINT + "get_api_documentation"
  );

  return {
    define: {
      "process.env.DEBUG": JSON.stringify(DEBUG),
      "process.env.REACT_APP_API_URL": JSON.stringify(REACT_APP_API_URL),
    },
    resolve: {
      extensions: [".js", ".jsx"],
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        [VITE_CRCON_API_ENDPOINT]: {
          target: VITE_CRCON_SERVER_URL,
          changeOrigin: true,
        },
      },
    },
    preview: {
      port: 3000,
      proxy: {
        [VITE_CRCON_API_ENDPOINT]: {
          target: VITE_CRCON_SERVER_URL,
          changeOrigin: true,
        },
      },
    },
    esbuild: {
      loader: "jsx",
      include: /src\/.*\.jsx?$/,
      exclude: [],
    },
    optimizeDeps: {
      esbuildOptions: {
        loader: { ".js": "jsx" },
        plugins: [
          {
            name: "load-js-files-as-jsx",
            setup(build) {
              build.onLoad({ filter: /src\/.*\.js$/ }, async (args) => ({
                loader: "jsx",
                contents: await fs.readFile(args.path, "utf8"),
              }));
            },
          },
        ],
      },
    },
  };
});
