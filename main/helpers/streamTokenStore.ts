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

const STORE_KEY = 'user.streamToken';

export const saveStreamToken = (token: any) => {
  console.log('saveStreamToken:', token);
  try {
    store.set(STORE_KEY, token);
  } catch (e) {
    console.error('Failed to save stream token:', e);
    try {
      store.set(STORE_KEY, {});
    } catch (innerError) {
      console.error('Failed to reset stream token:', innerError);
    }
  }
};

export const getStreamToken = (): any => {
  try {
    const token = store.get(STORE_KEY);
    if (!token) {
      return null;
    }
    return token;
  } catch (error) {
    console.error('Failed to get stream token:', error);
    return null;
  }
};

export const clearStreamToken = () => {
  try {
    store.set(STORE_KEY, {});
  } catch (error) {
    console.error('Failed to clear stream token:', error);
  }
};

export const isStreamTokenValid = (token: any) => {
  if (!token) {
    return false;
  }
  const {data, _objectCreateTime} = token;
  if (!data || !data.durationInSeconds) {
    return false;
  }
  return (
    _objectCreateTime + data.durationInSeconds * 1000 - new Date().getTime() >
    60 * 1000
  );
};
