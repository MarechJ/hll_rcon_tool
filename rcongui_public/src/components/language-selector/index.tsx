import { useTranslation } from 'react-i18next'
import { useCallback, useMemo } from 'react'
import { Languages } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { LANGUAGES } from '@/i18n/config'
import i18next from 'i18next'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Label } from '../ui/label'

const getLocaleDisplayName = (locale: string, displayLocale?: string) => {
  if (locale === 'en24h') {
    return 'English (24h)';
  } else if (locale === 'en') {
    return 'English (AM/PM)';
  }
  const displayName = new Intl.DisplayNames([displayLocale || locale], {
    type: 'language',
  }).of(locale)!
  return displayName.charAt(0).toLocaleUpperCase() + displayName.slice(1)
}

const DropdownLanguageSelector = () => {
  const { i18n } = useTranslation()
  const { t } = useTranslation('translation')

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
          <span className="sr-only">{t('selectLanguage')}</span>
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

const SelectLanguageSelector = () => {
  const { i18n } = useTranslation()
  const { t } = useTranslation('translation')
  return (
    <div>
      <Label className="flex flex-row gap-2 py-1" htmlFor="language-selector">
        <Languages className="size-4" />
        {t('selectLanguage')}
      </Label>
      <Select value={i18n.language} onValueChange={i18n.changeLanguage}>
        <SelectTrigger id="language-selector" className="w-full">
          <SelectValue placeholder={t('selectLanguage')} />
        </SelectTrigger>
        <SelectContent className="max-h-[200px]">
          {LANGUAGES.map((locale) => (
            <SelectItem key={locale} value={locale}>
              {getLocaleDisplayName(locale)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

export { DropdownLanguageSelector, SelectLanguageSelector }
