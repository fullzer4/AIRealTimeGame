import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    reactCompiler: true,
  },
  env: {
    NODE_ENV: "production",
  },
  output: "export",
  exportTrailingSlash: true,
  productionBrowserSourceMaps: false,
}

export default nextConfig
