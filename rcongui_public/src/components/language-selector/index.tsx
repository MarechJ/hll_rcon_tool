import { useTranslation } from 'react-i18next'
import { useCallback, useMemo } from 'react'
import { Languages } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { LANGUAGES } from '@/i18n/config'
import i18next from 'i18next'

const getLocaleDisplayName = (locale: string, displayLocale?: string) => {
  const displayName = new Intl.DisplayNames([displayLocale || locale], {
    type: 'language',
  }).of(locale)!
  return displayName.charAt(0).toLocaleUpperCase() + displayName.slice(1)
}

const LanguageSelector = () => {
  const { i18n } = useTranslation()

  const localesAndNames = useMemo(() => {
    return LANGUAGES.map((locale) => ({
      locale,
      name: getLocaleDisplayName(locale),
    }))
  }, [])

  const languageChanged = useCallback(async (locale: string) => {
    i18next.changeLanguage(locale)
  }, [])

  const { resolvedLanguage: currentLanguage } = i18n

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Languages className="h-[1.2rem] w-[1.2rem]" />
          <span className="sr-only">Select language</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {localesAndNames.map(({ locale, name }) => {
          const isSelected = currentLanguage === locale
          return (
            <DropdownMenuItem
              key={locale}
              onClick={() => languageChanged(locale)}
              className={cn(isSelected && 'font-bold text-primary')}
            >
              {name}
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export { LanguageSelector }
