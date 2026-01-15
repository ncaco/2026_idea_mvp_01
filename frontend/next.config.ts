import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  output: 'standalone',
  // Electron에서 사용할 때는 basePath와 assetPrefix 설정
  ...(process.env.ELECTRON === 'true' && {
    basePath: '',
    assetPrefix: './',
  }),
};

export default nextConfig;
