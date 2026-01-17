const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
// electron-updater는 선택사항이므로 try-catch로 처리
let autoUpdater;
try {
  autoUpdater = require('electron-updater').autoUpdater;
} catch (e) {
  console.log('electron-updater가 설치되지 않았습니다. 자동 업데이트 기능을 사용할 수 없습니다.');
}

let mainWindow;
let nextProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.join(__dirname, '../build/icon.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // 개발 모드에서는 Next.js 개발 서버 사용
  const isDev = process.env.NODE_ENV !== 'production';
  
  if (isDev) {
    // Next.js 개발 서버가 이미 실행 중이라고 가정
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    // 프로덕션 모드에서는 빌드된 Next.js 앱 사용
    const indexPath = path.join(__dirname, '../out/index.html');
    mainWindow.loadFile(indexPath).catch((err) => {
      console.error('Failed to load index.html:', err);
      // fallback: 상대 경로로 시도
      mainWindow.loadURL('file://' + indexPath);
    });
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 자동 업데이트 설정 (선택사항)
if (process.env.NODE_ENV === 'production' && autoUpdater) {
  autoUpdater.checkForUpdatesAndNotify();
  
  autoUpdater.on('update-available', () => {
    console.log('업데이트가 사용 가능합니다.');
  });
  
  autoUpdater.on('update-downloaded', () => {
    console.log('업데이트가 다운로드되었습니다. 재시작하면 적용됩니다.');
    autoUpdater.quitAndInstall();
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (nextProcess) {
    nextProcess.kill();
  }
});
