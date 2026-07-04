/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  reactStrictMode: false,
  // 核心：强制 Webpack 在服务器端打包时，遇到 document 或 window 直接用空对象代替，绝不报错！
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        document: false,
        window: false,
      };
    }
    return config;
  },
}

module.exports = nextConfig
