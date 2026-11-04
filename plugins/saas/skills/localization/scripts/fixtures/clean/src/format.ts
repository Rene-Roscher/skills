export const rateUnit = 'MB/s'

export function formatCount(count: number, locale: string): string {
  return new Intl.NumberFormat(locale).format(count)
}
