'use client'
import siteConfig from '@/lib/siteConfig'
import { cn } from '@/lib/utils'
import { useTranslation } from 'react-i18next'
import { Link, useLocation } from 'react-router-dom'

export function NavLinks() {
  const pathname = useLocation()
  const { t } = useTranslation('navigation')

  return siteConfig.navLinks.map((link) => {
    const isNotActive = pathname.pathname !== link.href
    return (
      <Link
        key={link.href}
        to={link.href}
        className={cn(
          'text-sm font-medium transition-colors',
          isNotActive && 'text-muted-foreground',
          !link.disabled && 'hover:text-primary',
          link.disabled && 'text-muted-foreground/50',
        )}
        aria-disabled={!!link.disabled}
      >
        {t(link.labelKey)}
      </Link>
    )
  })
}
