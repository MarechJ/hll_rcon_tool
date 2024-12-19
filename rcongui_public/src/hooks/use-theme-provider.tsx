import React, { createContext, useContext, useEffect, useState } from 'react'
import { Helmet } from 'react-helmet'

enum ThemeColor {
  LIGHT = '#ffffff',
  DARK = '#292524'
}

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextProps {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextProps | undefined>(undefined)

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'system',
  storageKey = 'ui-theme'
}): JSX.Element => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem(storageKey) as Theme | null
    return savedTheme || defaultTheme
  })

  // Apply the theme to the document
  useEffect(() => {
    const root = document.documentElement
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

    // Determine theme to apply
    const appliedTheme = theme === 'system' ? (systemPrefersDark ? 'dark' : 'light') : theme

    // Remove any existing theme classes and apply the new one
    root.classList.remove('light', 'dark')
    root.classList.add(appliedTheme)
  }, [theme])

  // Function to update the theme and persist it
  const setTheme = (newTheme: Theme) => {
    localStorage.setItem(storageKey, newTheme)
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Helmet>
        <meta name='theme-color' content={theme === 'dark' ? ThemeColor.DARK : ThemeColor.LIGHT} />
      </Helmet>
      {children}
    </ThemeContext.Provider>
  )
}

// Custom hook to access the theme context
export const useTheme = (): ThemeContextProps => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
