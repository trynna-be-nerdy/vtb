import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // ISR revalidation — category pages and meeting lists refresh every 15 min
  // Individual meeting detail pages revalidate on-demand (via cache invalidation)
  async rewrites() {
    return [];
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/updates",
  },
};

export default nextConfig;
