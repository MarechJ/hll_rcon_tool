'use client'

import { Moon, Sun, SunMoon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { useTheme } from '@/hooks/use-theme-provider'
import { useTranslation } from 'react-i18next'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Label } from '../ui/label'

function DropdownThemeToggle() {
  const { setTheme } = useTheme()
  const { t } = useTranslation('translation')

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant='outline' size='icon'>
          <Sun className='h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0' />
          <Moon className='absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100' />
          <span className='sr-only'>{t('toggleTheme')}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align='end'>
        <DropdownMenuItem onClick={() => setTheme('light')}>{t('themeMode.light')}</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')}>{t('themeMode.dark')}</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('system')}>{t('themeMode.system')}</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

const SelectThemeToggle = () => {
  const { t } = useTranslation('translation')
  const { theme, setTheme } = useTheme()

  return (
    <div>
      <Label className='flex flex-row gap-2 py-1' htmlFor='theme-selector'>
        <SunMoon className='size-4' />
        {t('toggleTheme')}
      </Label>
      <Select value={theme} onValueChange={setTheme}>
        <SelectTrigger id='theme-selector' className='w-full'>
          <SelectValue placeholder={t('toggleTheme')} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='light'>{t('themeMode.light')}</SelectItem>
          <SelectItem value='dark'>{t('themeMode.dark')}</SelectItem>
          <SelectItem value='system'>{t('themeMode.system')}</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}

export { DropdownThemeToggle, SelectThemeToggle }
