import { LANGUAGES } from './src/i18n/config'

export default {
  baseLocale: 'en',
  locales: LANGUAGES,
  localePath: 'src/i18n/locales',
  openAIApiKey: process.env.OPENAI_API_KEY,
  openAIApiUrl: process.env.OPENAI_API_URL,
}
