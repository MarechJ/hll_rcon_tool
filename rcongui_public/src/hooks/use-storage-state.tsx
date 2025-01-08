import {Dispatch, SetStateAction, useEffect, useState} from "react";

const prefix = 'public-crcon.';
const withPrefix = (key: string) => prefix + key

const getItem = (key: string) => {
  const item = localStorage.getItem(withPrefix(key));

  if (!item) {
    return null;
  }

  try {
    return JSON.parse(item);
  } catch (error) {
    console.error(`
        You most likely see this message due to an upgrade to a new version of this app.\n
        ${key} value in your local storage was not able to read.\n${key} has been reset.
        `);
    localStorage.removeItem(withPrefix(key));
  }
};

export function useStorageState<T> (key: string, initialState: T): [T, Dispatch<SetStateAction<T>>] {
  const [value, setValue] = useState<T>(
    getItem(key) ?? initialState
  );

  useEffect(() => {
    localStorage.setItem(withPrefix(key), JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
