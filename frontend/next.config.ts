import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone for optimized production builds
  output: "standalone",
  // Allow external images if needed
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
};

export default nextConfig;
