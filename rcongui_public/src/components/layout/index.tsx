import { Outlet } from 'react-router'
import Footer from '../footer'
import { Header } from '../header'
import { Helmet } from 'react-helmet'
import { publicInfoQueryOptions } from '@/lib/queries/public-info'
import { useTranslation } from 'react-i18next'
import { useSuspenseQuery } from '@tanstack/react-query'

export default function Layout() {
  const { data: publicInfo } = useSuspenseQuery(publicInfoQueryOptions)
  const { t } = useTranslation('translation')

  return (
    <>
      <Helmet defaultTitle={t('title')} titleTemplate={`%s | ${publicInfo?.name?.name ?? t('title')}`} />
      <div className="relative flex flex-col min-h-screen">
        <Header />
        <main className="container px-1 pb-10 sm:px-4 relative flex flex-col grow bg-background gap-1">
          <Outlet />
        </main>
        <Footer />
      </div>
    </>
  )
}
