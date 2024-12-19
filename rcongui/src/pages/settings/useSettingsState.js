import { useEffect, useMemo, useState, useRef } from 'react'
import { useActionData, useSubmit } from 'react-router-dom'

export const useSettingsState = (initialSettings) => {
  const [pendingSettings, setPendingSettings] = useState(initialSettings)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const submit = useSubmit()
  const actionData = useActionData()
  const lastSubmissionRef = useRef(null)

  useEffect(() => {
    setPendingSettings(initialSettings)
  }, [initialSettings])

  useEffect(() => {
    if (actionData && initialSettings) {
      if (lastSubmissionRef.current === actionData.cmd) {
        if (actionData.success) {
          setError(null)
          setPendingSettings(initialSettings)
        } else {
          setError(actionData.error)
        }
        setIsSubmitting(false)
        lastSubmissionRef.current = null
      }
    }
  }, [actionData, initialSettings])

  const isAltered = useMemo(() => {
    if (isSubmitting) return true
    if (typeof initialSettings === 'object') {
      for (const key in initialSettings) {
        if (initialSettings[key] !== pendingSettings[key]) {
          return true
        }
      }
    } else if (typeof initialSettings === 'string') {
      return initialSettings !== pendingSettings
    }
    return false
  }, [initialSettings, pendingSettings, isSubmitting])

  const handleSubmit = (payload, options) => {
    setIsSubmitting(true)
    lastSubmissionRef.current = payload.cmd
    submit(payload, options)
  }

  const handleReset = () => {
    setError(null)
    setPendingSettings(initialSettings)
  }

  return {
    pendingSettings,
    setPendingSettings,
    isSubmitting,
    error,
    setError,
    submit: handleSubmit,
    reset: handleReset,
    isAltered
  }
}
