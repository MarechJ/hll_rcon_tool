import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs/promises';
import path from 'path';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  console.log(JSON.stringify(env.REACT_APP_API_URL))

  return {
    define: {
      'process.env.REACT_APP_PUBLIC_BUILD': JSON.stringify(env.REACT_APP_PUBLIC_BUILD),
      'process.env.REACT_APP_API_URL': JSON.stringify(env.REACT_APP_API_URL),
      'process.env.DEBUG': JSON.stringify(env.DEBUG),
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
        '/api': {
          target: 'http://192.168.4.30:8010',
          changeOrigin: true,
        },
      },
    },
    preview: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://192.168.4.30:8010',
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
