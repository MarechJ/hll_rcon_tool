import { cn } from '@/lib/utils'
import { NavLinks } from './nav-links'

export function MainNav({ className, ...props }: React.HTMLAttributes<HTMLElement>) {
  return (
    <nav className={cn('hidden md:flex items-center [&>*]:text-nowrap', className)} {...props}>
      <NavLinks />
    </nav>
  )
}
