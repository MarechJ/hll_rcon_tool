import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { cmd, get, handleHttpError } from '@/utils/fetchUtils';

export const useTemplates = (key, initialState = []) => {
  const [texts, setTexts] = React.useState(initialState);
  // Fetch remote texts using useQuery
  const { data: remoteTexts, isLoading, isError } = useQuery({
    queryKey: ['message-templates', key], // Query key
    queryFn: async () => {
      try {
        const response = await get(`${cmd.GET_MESSAGE_TEMPLATE}?category=${key.toUpperCase()}`)
        handleHttpError(response)
        const data = await response.json()
        if (data && data.result && !data.failed) {
          return data.result
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


  return { value: mergedTexts };
};
