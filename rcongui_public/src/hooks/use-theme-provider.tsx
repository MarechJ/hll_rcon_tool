import React, { createContext, useContext, useEffect, useState } from 'react'
import { Helmet } from 'react-helmet'

enum ThemeColor {
  LIGHT = '#ffffff',
  DARK = '#292524',
}

type Theme = 'light' | 'dark' | 'system'
type ResolvedTheme = 'light' | 'dark'

interface ThemeContextProps {
  theme: Theme
  resolvedTheme: ResolvedTheme
  setTheme: (theme: Theme) => void
}

const getSystemTheme = (): ResolvedTheme =>
  window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'

const ThemeContext = createContext<ThemeContextProps | undefined>(undefined)

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'system',
  storageKey = 'ui-theme',
}) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem(storageKey) as Theme | null
    return savedTheme || defaultTheme
  })

  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>(() =>
    theme === 'system' ? getSystemTheme() : theme
  )

  // Apply the theme to the document
  useEffect(() => {
    const root = document.documentElement

    const applyTheme = () => {
      const appliedTheme = theme === 'system' ? getSystemTheme() : theme
      root.classList.remove('light', 'dark')
      root.classList.add(appliedTheme)
      setResolvedTheme(appliedTheme)
    }

    applyTheme()

    // keep it in sync if the OS theme changes while "system" is selected
    if (theme === 'system') {
      const mql = window.matchMedia('(prefers-color-scheme: dark)')
      mql.addEventListener('change', applyTheme)
      return () => mql.removeEventListener('change', applyTheme)
    }

    return undefined
  }, [theme])

  // Function to update the theme and persist it
  const setTheme = (newTheme: Theme) => {
    localStorage.setItem(storageKey, newTheme)
    setThemeState(newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      <Helmet>
        <meta name="theme-color" content={resolvedTheme === 'dark' ? ThemeColor.DARK : ThemeColor.LIGHT} />
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
