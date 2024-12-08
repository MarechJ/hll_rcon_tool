import { cn } from '@shared/utils';
import { NavLinks } from '../nav-links';

export function MainNav({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) {
  return (
    <nav
      className={cn('hidden md:flex items-center space-x-4 lg:space-x-6 [&>*]:text-nowrap', className)}
      {...props}
    >
      <NavLinks />
    </nav>
  );
}
