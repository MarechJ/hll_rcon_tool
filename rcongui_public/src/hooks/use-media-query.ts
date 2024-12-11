import { useState, useEffect } from 'react'

export default function useMediaQuery(query: string): boolean {
  const [isMatch, setIsMatch] = useState<boolean>(false)

  useEffect(() => {
    const mediaQueryList = window.matchMedia(query)
    const documentChangeHandler = () => setIsMatch(mediaQueryList.matches)

    // Set the initial state
    documentChangeHandler()

    // Add event listener
    mediaQueryList.addEventListener('change', documentChangeHandler)

    // Clean up event listener on unmount
    return () => {
      mediaQueryList.removeEventListener('change', documentChangeHandler)
    }
  }, [query])

  return isMatch
}
