type SiteConfig = {
  crconGitUrl: string;
  navLinks: { href: string; label: string; disabled?: boolean }[];
};

const siteConfig: SiteConfig = {
  crconGitUrl: 'https://github.com/MarechJ/hll_rcon_tool',
  navLinks: [
    {
      href: '/',
      label: 'Live Game',
    },
    {
      href: '/matches',
      label: 'Last Games',
    },
  ],
};

export default siteConfig;
