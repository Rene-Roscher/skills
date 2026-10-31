#!/bin/sh
set -eu
mkdir -p tests/e2e
cat > package.json <<'JSON'
{ "private": true, "type": "module", "devDependencies": { "@playwright/test": "^1.61.0" } }
JSON
cat > tests/e2e/invite.spec.ts <<'TS'
import { test, expect } from '@playwright/test'

test('sending an invite shows one toast', async ({ page }) => {
  await page.goto('/projects/demo/members')
  await page.getByTestId('invite-email').fill('new.member@example.com')
  await page.getByTestId('invite-send').click()
  const toasts = await page.getByTestId('toast').count()
  expect(toasts).toBe(1)
})
TS
