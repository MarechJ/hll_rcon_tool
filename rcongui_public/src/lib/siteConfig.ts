import type resources from '../types/resources'

type NavigationKeys = keyof (typeof resources)['navigation']

const siteConfig = {
  crconGitUrl: 'https://github.com/MarechJ/hll_rcon_tool',
  teamName: 'CRCON Team',
  navLinks: [
    {
      href: '/',
      labelKey: 'currentGame'
    },
    {
      href: '/games',
      labelKey: 'gameHistory'
    }
  ] as { href: string; labelKey: NavigationKeys; disabled?: boolean }[]
}

export default siteConfig
