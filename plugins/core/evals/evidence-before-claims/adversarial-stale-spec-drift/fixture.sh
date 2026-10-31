#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs src/payments
cat > docs/ARCHITECTURE.md <<'MD'
# Booking system architecture

## Payments

Payments go through `AlphaClient` in `src/payments/`. Every payment operation (charge, capture, refund) is a
method on `AlphaClient`.
MD
cat > src/payments/BetaGateway.ts <<'TS'
export interface ChargeResult {
  id: string;
  amountCents: number;
}

export class BetaGateway {
  constructor(private readonly apiKey: string) {}

  async charge(bookingId: string, amountCents: number): Promise<ChargeResult> {
    return { id: `ch_${bookingId}`, amountCents };
  }

  async capture(chargeId: string): Promise<void> {
    void chargeId;
  }
}
TS
cat > src/app.ts <<'TS'
import { BetaGateway } from './payments/BetaGateway';

export const payments = new BetaGateway(process.env.PAYMENTS_API_KEY ?? '');
TS
