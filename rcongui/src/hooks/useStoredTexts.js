import React from 'react';
import localforage from 'localforage';
import { useQuery } from '@tanstack/react-query';
import { get, handleHttpError } from '@/utils/fetchUtils';

// Async function to get item from localforage
const getItem = async (key) => {
  try {
    const value = await localforage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.error(`
        You most likely see this message due to an upgrade to a new version of this app.\n
        ${key} value in your local storage was not able to be read.\n${key} has been reset.
    `);
    await localforage.removeItem(key); // Reset the key in case of an error
    return null;
  }
};

export const useStoredTexts = (key, initialState = []) => {
  const [texts, setTexts] = React.useState(initialState);
  // Fetch remote texts using useQuery
  const { data: remoteTexts, isLoading, isError } = useQuery({
    queryKey: ['shared-messages', key], // Query key
    queryFn: async () => {
      try {
        const response = await get(`get_standard_${key}_messages`)
        handleHttpError(response)
        const data = await response.json()
        if (data && data.result && !data.failed) {
          return data.result.messages.map(text => {
            let title = text.substring(0, 16);
            if (text.length > 16) {
              title += "...";
            }
            return { title, content: text }
          })
        }
      } catch (error) {
        console.error(error)
      }
      return [];
    },
    // retry: false,
    initialData: [],
    // staleTime: 5 * 60 * 1000,
  });

  const mergedTexts = texts.concat(remoteTexts)

  // Use React.useEffect to load the data initially (local + remote merge)
  React.useEffect(() => {
    const fetchData = async () => {
      // Get local texts from localforage
      const storedValue = await getItem(key);
      // If local data exists, merge it with the remote data
      if (storedValue !== null) {
        setTexts(storedValue);
      }
    };

    fetchData();
  }, [key]);


  // Store the value asynchronously whenever it changes
  React.useEffect(() => {
    const saveData = async () => {
      try {
        await localforage.setItem(key, JSON.stringify(texts));
      } catch (error) {
        console.error('Failed to save value in localforage:', error);
      }
    };
    saveData();
  }, [key, texts]);

  const addText = (message) => {
    setTexts(prev => prev.slice().concat(message))
  }

  const removeText = (index) => {
    setTexts(prev => prev.slice(0, index).concat(prev.slice(index + 1)))
  }

  const editText = (index, newMessage) => {
    setTexts(prev => prev.slice(0, index).concat([newMessage].concat(prev.slice(index + 1))))
  }

  return { value: mergedTexts, addText, removeText, editText };
};
