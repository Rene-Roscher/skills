#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
cat > tools.json <<'JSON'
{
  "tools": [
    {
      "name": "find_bookings",
      "title": "Find bookings",
      "description": "Search bookings. Never writes.",
      "annotations": {
        "readOnlyHint": true
      },
      "inputSchema": {
        "type": "object",
        "properties": {
          "customer": {
            "type": "string"
          }
        },
        "additionalProperties": false
      }
    },
    {
      "name": "manage_booking",
      "title": "Manage booking",
      "description": "Create, update, cancel or notify a booking.",
      "annotations": {},
      "inputSchema": {
        "type": "object",
        "properties": {
          "action": {
            "enum": [
              "create",
              "update",
              "cancel",
              "notify"
            ]
          },
          "organization_id": {
            "type": "string"
          },
          "booking_id": {
            "type": "string"
          }
        },
        "additionalProperties": false
      }
    },
    {
      "name": "send_confirmation",
      "title": "Send confirmation",
      "description": "Send the confirmation mail.",
      "annotations": {
        "readOnlyHint": true
      },
      "inputSchema": {
        "type": "object",
        "properties": {
          "booking_id": {
            "type": "string"
          }
        },
        "additionalProperties": false
      }
    }
  ]
}
JSON
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add tools list dump'
