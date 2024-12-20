import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    reactCompiler: true,
  },
  output: "export",
  exportTrailingSlash: true,
  productionBrowserSourceMaps: false,
}

export default nextConfig
