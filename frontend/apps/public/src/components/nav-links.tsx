'use client';
import Link from 'next/link';
import siteConfig from '../utils/siteConfig';
import { cn } from '@shared/utils';
import { usePathname } from 'next/navigation';

export function NavLinks() {
  const pathname = usePathname();

  return siteConfig.navLinks.map((link) => {
    const isNotActive = pathname !== link.href;
    return (
      <Link
        key={link.href}
        href={link.href}
        className={cn(
          'text-sm font-medium transition-colors',
          isNotActive && 'text-muted-foreground',
          !link.disabled && 'hover:text-primary',
          link.disabled && 'text-muted-foreground/50'
        )}
        aria-disabled={!!link.disabled}
      >
        {link.label}
      </Link>
    );
  });
}
