import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  distDir: 'out',
  images: {
    unoptimized: true
  },
  assetPrefix: process.env.NODE_ENV === 'production' ? '/static' : '',
  basePath: process.env.NODE_ENV === 'production' ? '/static' : '',
  allowedDevOrigins: ['0.0.0.0'],
};

export default nextConfig;
