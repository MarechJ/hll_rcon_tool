import {useTranslation} from "react-i18next";
import dayjs from "dayjs";
import {createContext, ReactNode, useContext, useEffect} from "react";
import 'dayjs/locale/en';
import 'dayjs/locale/de';
import 'dayjs/locale/fr';
import 'dayjs/locale/es';
import 'dayjs/locale/zh';
import 'dayjs/locale/ja';
import 'dayjs/locale/ko';
import 'dayjs/locale/pt';
import 'dayjs/locale/it';
import 'dayjs/locale/ru';
import 'dayjs/locale/cs';
import {DAYJS_LANGUAGES} from "@/i18n/config";
import localizedFormat from "dayjs/plugin/localizedFormat";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import localeData from "dayjs/plugin/localeData";

dayjs.extend(localizedFormat);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(localeData);
// mix 'en' date related translations with 'it' date format
dayjs.locale('en24h', {
  ...dayjs.Ls.en,
  formats: {
    ...dayjs.Ls.it.formats,
  },
});

interface LocaleContextType {
  globalLocaleData: dayjs.GlobalLocaleDataReturn;
}

const LocaleContext = createContext<LocaleContextType | null>(null);

export const useLocale = () => {
  const context = useContext(LocaleContext);

  if (!context) {
    throw new Error('useLocale must be used within a LocaleProvider');
  }

  return context;
};

/**
 * handles localization of dayjs
 */
export const LocaleProvider = ({ children }: { children: ReactNode}) => {

  const { i18n } = useTranslation();

  const handleLanguageChanged = () => {
    const userLocale = i18n.language.split('-')[0];
    const selectedLocale = DAYJS_LANGUAGES.includes(userLocale) ? userLocale : 'en';
    dayjs.locale(selectedLocale);
  };

  useEffect(() => {
    handleLanguageChanged();
    i18n.on('languageChanged', handleLanguageChanged);
    return () => {
      i18n.off('languageChanged', handleLanguageChanged);
    };
  }, [handleLanguageChanged]);

  const globalLocaleData = dayjs.localeData();

  return (
    <LocaleContext.Provider value={{ globalLocaleData }}>
      {children}
    </LocaleContext.Provider>
  );
};
