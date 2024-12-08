import { useState, useEffect } from 'react'

type UseLocalStorageStateHook<T> = [T, React.Dispatch<React.SetStateAction<T>>]

function useLocalStorageState<T>(key: string, initialValue: T): UseLocalStorageStateHook<T> {
  const [state, setState] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(`Unable to get value from localStorage for key "${key}":`, error)
      return initialValue
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state))
    } catch (error) {
      console.error(`Unable to set value to localStorage for key "${key}":`, error)
    }
  }, [key, state])

  return [state, setState]
}

export default useLocalStorageState
