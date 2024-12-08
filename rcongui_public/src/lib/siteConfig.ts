import type resources from '../types/resources'

type NavigationKeys = keyof (typeof resources)['navigation']

type SiteConfig = {
  crconGitUrl: string
  navLinks: { href: string; labelKey: NavigationKeys; disabled?: boolean }[]
}

const siteConfig: SiteConfig = {
  crconGitUrl: 'https://github.com/MarechJ/hll_rcon_tool',
  navLinks: [
    {
      href: '/',
      labelKey: 'currentGame',
    },
    {
      href: '/history',
      labelKey: 'gameHistory',
    },
  ],
}

export default siteConfig
