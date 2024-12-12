import { NavLinks } from './nav-links'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { MenuIcon } from 'lucide-react'
import { ServerName } from './server-name'

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
      <SheetContent side={'left'}>
        <SheetHeader className="text-wrap text-left mb-8 pr-4">
          <SheetTitle>
            <ServerName />
          </SheetTitle>
        </SheetHeader>
        <nav className="flex flex-col gap-4 [&>*]:block [&>*]:text-lg">
          <NavLinks />
        </nav>
      </SheetContent>
    </Sheet>
  )
}
