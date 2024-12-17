import siteConfig from '@/config/siteConfig'
import { useEffect, useState } from 'react'

const prefix = siteConfig.appName + '.'
const withPrefix = (key) => prefix + key

const getItem = (key) => {
  try {
    return JSON.parse(localStorage.getItem(withPrefix(key)))
  } catch (error) {
    console.error(`
        You most likely see this message due to an upgrade to a new version of this app.\n
        ${key} value in your local storage was not able to read.\n${key} has been reset.
        `)
    localStorage.removeItem(withPrefix(key))
  }
}

export const useStorageState = (key, initialState) => {
  const [value, setValue] = useState(getItem(key) ?? initialState)

  useEffect(() => {
    localStorage.setItem(withPrefix(key), JSON.stringify(value))
  }, [key, value])

  return [value, setValue]
}
