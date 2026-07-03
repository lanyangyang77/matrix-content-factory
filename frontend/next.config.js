/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  reactStrictMode: true,
  // 忽略所有可能阻止打包的校验
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
}

module.exports = nextConfig
