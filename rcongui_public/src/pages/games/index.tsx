import MatchesList from './list'
import { useSearchParams } from 'react-router-dom'
import { Helmet } from 'react-helmet'
import { useTranslation } from 'react-i18next'

export default function MatchesPage() {
  const { t } = useTranslation('navigation')
  const [searchParams] = useSearchParams()
  const page = Number(searchParams.get('page') ?? 1)
  const pageSize = Number(searchParams.get('page_size') ?? 50)

  return (
    <>
      <Helmet>
        <title>{t('gameHistory')}</title>
      </Helmet>
      <MatchesList page={page} pageSize={pageSize} />
    </>
  )
}
