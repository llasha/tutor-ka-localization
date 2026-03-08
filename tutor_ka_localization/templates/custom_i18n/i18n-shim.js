import * as languages from 'i18n-iso-languages';
import kaLangData from './ka.json';

if (!globalThis.__KA_I18N_INITIALIZED__) {
  languages.registerLocale(kaLangData);
  globalThis.__KA_I18N_INITIALIZED__ = true;
}

export default languages;
export * from 'i18n-iso-languages';

