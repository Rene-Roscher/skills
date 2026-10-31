#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p src/Mcp
cat > src/Mcp/SendConfirmationTool.php <<'PHP'
<?php
// Sends the booking confirmation mail right away. The tenant comes from the argument.
class SendConfirmationTool
{
    public function handle(array $args): array
    {
        $booking = Booking::where('organization_id', $args['organization_id'])->findOrFail($args['booking_id']);
        Mail::to($booking->customer->email)->send(new BookingConfirmation($booking));
        return ['ok' => true];
    }
}
PHP
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'feat: add confirmation tool'
