import { useTranslation } from 'react-i18next'
import { isRouteErrorResponse, Link, useRouteError } from 'react-router'
import { Button } from '../ui/button'

export default function ErrorPage() {
  const error = useRouteError()
  const { t } = useTranslation('notfound')
  let errorMessage: string

  if (isRouteErrorResponse(error)) {
    // error is type `ErrorResponse`
    errorMessage = error.data || error.statusText
  } else if (error instanceof Error) {
    errorMessage = error.message
  } else if (typeof error === 'string') {
    errorMessage = error
  } else {
    console.error(error)
    errorMessage = 'Unknown error'
  }

  return (
    <div className="flex h-screen w-full flex-col items-center justify-center gap-4 text-left">
      <h1>{t('oops')}</h1>
      <p>{t('title')}</p>
      <p className="font-mono">
        <i>{errorMessage}</i>
      </p>
      <Button asChild>
        <Link to="/">{t('backtohomepage')}</Link>
      </Button>
    </div>
  )
}
