import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  // Electron 빌드를 위해 export 모드 사용
  output: process.env.ELECTRON === 'true' ? 'export' : 'standalone',
  // Electron에서 사용할 때는 basePath와 assetPrefix 설정
  ...(process.env.ELECTRON === 'true' && {
    basePath: '',
    assetPrefix: './',
    images: {
      unoptimized: true,
    },
  }),
};

export default nextConfig;
