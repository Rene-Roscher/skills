#!/usr/bin/env bash
set -euo pipefail
cat > spec-released.yaml <<'YAML'
openapi: 3.1.0
info: { title: Bookings API, version: 1.4.0 }
paths:
  /v1/bookings:
    get:
      parameters:
        - { name: resource, in: query, required: false, schema: { type: string } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  id: { type: string }
                  start: { type: string, format: date-time }
YAML
cat > spec-next.yaml <<'YAML'
openapi: 3.1.0
info: { title: Bookings API, version: 1.5.0 }
paths:
  /v1/bookings:
    get:
      parameters:
        - { name: resource, in: query, required: true, schema: { type: string } }
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  id: { type: string }
                  starts_at: { type: string, format: date-time }
                  notes: { type: string }
YAML
