import siteConfig from '@/config/siteConfig';
import {useEffect, useState} from "react";
import deepmerge from 'lodash/merge';

const STORAGE_VERSION = '1.0'; // Define current version
const prefix = siteConfig.appName + '.';
const withPrefix = (key) => prefix + key;

const getItem = (key) => {
  try {
    const storedValue = localStorage.getItem(withPrefix(key));
    if (!storedValue) return null;
    
    const parsed = JSON.parse(storedValue);
    
    // Check if stored data has version information
    if (!parsed._version) {
      // No version - treat as legacy data
      localStorage.removeItem(withPrefix(key));
      return null;
    }

    // Version mismatch
    if (parsed._version !== STORAGE_VERSION) {
      console.info(`
        Storage version mismatch for ${key}.\n
        Stored: ${parsed._version}, Current: ${STORAGE_VERSION}\n
        Migrating data...
      `);
      localStorage.removeItem(withPrefix(key));
      return null;
    }

    return parsed.data;
  } catch (error) {
    console.error(`
      Storage read error for ${key}.\n
      Error: ${error.message}\n
      Storage has been reset.
    `);
    localStorage.removeItem(withPrefix(key));
    return null;
  }
};

const setItem = (key, value) => {
  const storageData = {
    _version: STORAGE_VERSION,
    data: value
  };
  localStorage.setItem(withPrefix(key), JSON.stringify(storageData));
};

export const useStorageState = (key, initialState) => {
  const [value, setValue] = useState(() => {
    const storedValue = getItem(key);
    
    if (storedValue && typeof initialState === 'object') {
      // Deep merge stored value with initial state
      return deepmerge({}, initialState, storedValue);
    }
    
    return storedValue ?? initialState;
  });

  useEffect(() => {
    setItem(key, value);
  }, [key, value]);

  return [value, setValue];
};
