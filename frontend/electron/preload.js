const { contextBridge } = require('electron');

// Electron API를 렌더러 프로세스에 안전하게 노출
contextBridge.exposeInMainWorld('electron', {
  // 필요한 Electron API를 여기에 추가
  platform: process.platform,
});
