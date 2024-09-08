import React from 'react';

const getItem = (key) => {
  try {
    return JSON.parse(localStorage.getItem(key));
  } catch (error) {
    console.error(`
        You most likely see this message due to an upgrade to a new version of this app.\n
        ${key} value in your local storage was not able to read.\n${key} has been reset.
        `);
    localStorage.removeItem(key);
    return;
  }
};

export const useStorageState = (key, initialState) => {
  const [value, setValue] = React.useState(
    getItem(key) ?? initialState
  );

  React.useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
};