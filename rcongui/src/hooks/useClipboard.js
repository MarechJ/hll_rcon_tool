import { useState, useEffect } from 'react';

export function useClipboard(duration = 2000) {
  const [isClipboardAvailable, setIsClipboardAvailable] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    // Check if the Clipboard API is available
    setIsClipboardAvailable(
      navigator?.clipboard !== undefined &&
        typeof navigator?.clipboard?.writeText === "function"
    );
  }, []);

  useEffect(() => {
    if (isCopied) {
      const timer = setTimeout(() => {
        setIsCopied(false);
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [isCopied, duration]);

  const copyToClipboard = async (text) => {
    if (isClipboardAvailable) {
      try {
        await navigator.clipboard.writeText(text);
        setIsCopied(true);
        return true;
      } catch (error) {
        console.error('Failed to copy:', error);
        return false;
      }
    }
    return false;
  };

  return {
    isClipboardAvailable,
    isCopied,
    copyToClipboard
  };
} 