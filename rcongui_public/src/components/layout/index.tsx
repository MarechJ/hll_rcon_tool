import { Outlet } from 'react-router-dom'
import Footer from '../footer'
import { Header } from '../header'
import { Helmet } from 'react-helmet'
import { usePublicInfo } from '@/lib/queries/public-info'
import { useTranslation } from 'react-i18next'

export default function Layout() {
  const [publicInfo] = usePublicInfo()
  const { t } = useTranslation('translation')

  return (
    <>
      <Helmet defaultTitle={t('title')} titleTemplate={`%s | ${publicInfo?.name?.name ?? t('title')}`} />
      <div className="relative flex min-h-screen flex-col">
        <Header />
        <main className="container px-1 mb-10 sm:px-4 relative flex min-h-screen flex-col bg-background gap-1">
          <Outlet />
        </main>
        <Footer />
      </div>
    </>
  )
}
