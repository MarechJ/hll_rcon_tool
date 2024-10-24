//@ts-check

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { composePlugins, withNx } = require('@nx/next');

/**
 * @type {import('@nx/next/plugins/with-nx').WithNxOptions}
 **/
const nextConfig = {
  nx: {
    // Set this to true if you would like to use SVGR
    // See: https://github.com/gregberge/svgr
    svgr: false,
  },
  distDir: 'dist',
  async rewrites() {
    return [
      {
        source: '/api/:slug*',
        destination: `${process.env.CRCON_URL ?? "http://localhost:8000"}/api/:slug*`, // Change this to your actual API endpoint
      },
    ];
  }
};

const plugins = [
  // Add more Next.js plugins to this list if needed.
  withNx,
];

module.exports = composePlugins(...plugins)(nextConfig);
