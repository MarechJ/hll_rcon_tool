import {defineConfig, loadEnv} from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs/promises';
import { pigment } from '@pigment-css/vite-plugin';

/**
 * @type {import('@pigment-css/vite-plugin').PigmentOptions}
 */
const pigmentConfig = {
  transformLibraries: ['@mui/material'],
};

export default defineConfig(({command, mode}) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    define: {
      'process.env.REACT_APP_PUBLIC_BUILD': env.REACT_APP_PUBLIC_BUILD,
      'process.env.REACT_APP_API_URL': `"${env.REACT_APP_API_URL}"`,
    },
    plugins: [
      pigment(pigmentConfig),
      react()
    ],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      }
    },
    esbuild: {
      loader: "jsx",
      include: /src\/.*\.jsx?$/,
      exclude: [],
    },
    optimizeDeps: {
      esbuildOptions: {
        loader: {'.js': 'jsx'},
        plugins: [
          {
            name: "load-js-files-as-jsx",
            setup(build) {
              build.onLoad({filter: /src\/.*\.js$/}, async (args) => ({
                loader: "jsx",
                contents: await fs.readFile(args.path, "utf8"),
              }));
            },
          },
        ],
      },
    },
  }
});
