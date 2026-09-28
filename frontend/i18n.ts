import { getRequestConfig } from "next-intl/server";
import { notFound } from "next/navigation";

export const locales = ["bs", "hr", "sr", "en", "de"] as const;
export const defaultLocale = "bs";
export type Locale = (typeof locales)[number];

export default getRequestConfig(async ({ locale }) => {
  const selectedLocale = locale ?? defaultLocale;
  if (!locales.includes(selectedLocale as Locale)) notFound();
  return {
    locale: selectedLocale,
    messages: (await import(`./messages/${selectedLocale}.json`)).default,
  };
});
