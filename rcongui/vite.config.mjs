import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs/promises';
import path from 'path';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  console.log("[dev] Requests to:", env.VITE_API_ENDPOINT, "will be proxied to:", env.VITE_CRCON_SERVER_URL);
  console.log("[dev] API Documentation:", env.VITE_CRCON_SERVER_URL + env.VITE_API_ENDPOINT + "get_api_documentation");

  return {
    define: {
      'process.env.API_ENDPOINT': JSON.stringify(env.VITE_API_ENDPOINT),
      'process.env.CRCON_SERVER_URL': JSON.stringify(env.VITE_CRCON_SERVER_URL),
      'process.env.DEBUG': JSON.stringify(env.DEBUG),
      'process.env.REACT_APP_API_URL': JSON.stringify(env.REACT_APP_API_URL),
    },
    resolve: {
      extensions: ['.js', '.jsx'],
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    plugins: [
      react(),
    ],
    server: {
      port: 3000,
      proxy: {
        [env.VITE_API_ENDPOINT]: {
          target: env.VITE_CRCON_SERVER_URL,
          changeOrigin: true,
        },
      },
    },
    preview: {
      port: 3000,
      proxy: {
        [env.VITE_API_ENDPOINT]: {
          target: env.VITE_CRCON_SERVER_URL,
          changeOrigin: true,
        },
      },
    },
    esbuild: {
      loader: 'jsx',
      include: /src\/.*\.jsx?$/,
      exclude: [],
    },
    optimizeDeps: {
      esbuildOptions: {
        loader: { '.js': 'jsx' },
        plugins: [
          {
            name: 'load-js-files-as-jsx',
            setup(build) {
              build.onLoad({ filter: /src\/.*\.js$/ }, async (args) => ({
                loader: 'jsx',
                contents: await fs.readFile(args.path, 'utf8'),
              }));
            },
          },
        ],
      },
    },
  };
});
