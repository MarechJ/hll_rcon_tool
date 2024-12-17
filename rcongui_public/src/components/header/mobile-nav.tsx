import { NavLinks } from './nav-links'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { MenuIcon } from 'lucide-react'
import { ServerName } from './server-name'
import { SelectLanguageSelector } from '../language-selector'
import { SelectThemeToggle } from '../theme-toggle'

export function MobileNav() {

  return (
    <Sheet>
      <SheetTrigger asChild className="md:hidden">
        <div>
          <Button variant="outline" size={'icon'} className="size-8">
            <MenuIcon />
          </Button>
        </div>
      </SheetTrigger>
      <SheetContent side={'left'} className="flex flex-col">
        <SheetHeader className="text-wrap text-left mb-8 pr-4">
          <SheetTitle>
            <ServerName />
          </SheetTitle>
        </SheetHeader>
        <nav tabIndex={0} className="flex flex-col grow gap-4">
          <ul className="flex flex-col [&>*]:block gap-4 [&>*]:text-lg">
            <NavLinks />
          </ul>
          <div className="h-[1px] w-full bg-border" />
          <div className="grow" />
          <div className="flex flex-col gap-2">
            <SelectThemeToggle />
            <SelectLanguageSelector />
          </div>
        </nav>
      </SheetContent>
    </Sheet>
  )
}
