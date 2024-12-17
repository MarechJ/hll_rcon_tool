import { DropdownThemeToggle } from '../theme-toggle'
import { DropdownLanguageSelector } from '../language-selector'

export function NavButtons() {
  return (
    <div className='hidden md:flex items-center space-x-1 [&>*]:size-8'>
      <DropdownLanguageSelector />
      <DropdownThemeToggle />
    </div>
  )
}
