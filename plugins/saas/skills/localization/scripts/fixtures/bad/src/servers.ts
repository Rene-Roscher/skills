export function summary(count: number): string {
  return count + ' servers found'
}

export const hint = 'Select item(s) to continue'

export const expiring = (count: number) => `${count} ` + t('certificates.expiring')

export const status = (name: string) => t('servers.status.prefix') + ' ' + name + t('servers.status.suffix')
