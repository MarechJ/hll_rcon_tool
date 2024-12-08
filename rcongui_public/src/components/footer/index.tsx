import { useTranslation } from 'react-i18next'

export default function Footer() {
  const { t } = useTranslation('translation')

  return (
    <footer className="bg-primary text-primary-foreground">
      <div className="flex flex-wrap items-center md:justify-between justify-center">
        <div className="w-full md:w-4/12 px-4 mx-auto text-center">
          <div className="text-sm font-semibold py-1">
            {t('made-by')}{' '}
            <a
              href="https://github.com/MarechJ/hll_rcon_tool"
              className="tracking-widest uppercase hover:text-secondary"
              target="_blank"
              rel="noreferrer"
            >
              CRCON Team
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
