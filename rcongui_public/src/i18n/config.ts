import i18next from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import resourcesToBackend from 'i18next-resources-to-backend'

export const LANGUAGES = ['en24h', 'en', 'de', 'fr', 'es', 'zh-Hans', 'zh-Hant', 'ja', 'ko', 'pt', 'it', 'ru', 'cs']

/**
 *  Also add import in {@link LocaleHandler}
 */
export const DAYJS_LANGUAGES = ['en24h', 'en', 'de', 'fr', 'es', 'zh', 'ja', 'ko', 'pt', 'it', 'ru', 'cs'];

i18next
  .use(LanguageDetector)
  .use(initReactI18next)
  .use(
    resourcesToBackend((language: string, namespace: string) => {
      // 'en24h' and 'en' are exactly the same for i18n. It has only an effect on dayjs
      const lang = language === 'en24h' ? 'en' : language;

      if (language === 'dev') return
      return import(`./locales/${lang}/${namespace}.json`)
    }),
  )
  .init({
    debug: import.meta.env.DEV,
    fallbackLng: {
      'de-CH': ['fr', 'it'],
      default: ['en24h'],
    },
  })
