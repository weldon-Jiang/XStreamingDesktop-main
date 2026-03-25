import Store from 'electron-store';
import { app } from 'electron';
import fs from 'fs';

// 确保存储目录存在
function ensureUserDataDir() {
  try {
    const userDataPath = app.getPath('userData');
    if (!fs.existsSync(userDataPath)) {
      fs.mkdirSync(userDataPath, { recursive: true });
    }
  } catch (error) {
    console.error('Failed to create user data directory:', error);
  }
}

// 确保目录存在后再创建store
ensureUserDataDir();
const store = new Store();

const STORE_KEY = 'user.webToken';

export const saveWebToken = (token: any) => {
  console.log('saveStreamToken:', token);
  try {
    store.set(STORE_KEY, token);
  } catch (e) {
    console.error('Failed to save web token:', e);
    try {
      store.set(STORE_KEY, {});
    } catch (innerError) {
      console.error('Failed to reset web token:', innerError);
    }
  }
};

export const getWebToken = (): any => {
  try {
    const token = store.get(STORE_KEY);
    if (!token) {
      return null;
    }
    return token;
  } catch (error) {
    console.error('Failed to get web token:', error);
    return null;
  }
};

export const clearWebToken = () => {
  try {
    store.set(STORE_KEY, {});
  } catch (error) {
    console.error('Failed to clear web token:', error);
  }
};

const calculateSecondsLeft = (date: any) => {
  const expiresOn = date;
  const currentDate = new Date();
  return Math.floor((expiresOn.getTime() - currentDate.getTime()) / 1000);
};

export const isWebTokenValid = (token: any) => {
  if (!token || !token.data || !token.data.NotAfter) {
    return false;
  }
  if (calculateSecondsLeft(new Date(token.data.NotAfter)) <= 0) {
    return false;
  }

  return true;
};
