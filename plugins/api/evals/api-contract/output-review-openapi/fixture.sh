#!/usr/bin/env bash
set -euo pipefail
cat > openapi.yaml <<'YAML'
openapi: 3.1.0
info:
  title: Bookings API
  version: 1.0.0
paths:
  /bookings:
    get:
      parameters:
        - name: page
          in: query
          schema: { type: integer }
      responses:
        "200":
          description: All bookings
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/Booking" }
    post:
      requestBody:
        content:
          application/json:
            schema: { $ref: "#/components/schemas/Booking" }
      responses:
        "200":
          description: Created
        "400":
          description: Error
          content:
            application/json:
              schema:
                type: object
                properties:
                  error: { type: string }
components:
  schemas:
    Booking:
      type: object
      properties:
        id: { type: integer }
        customer_id: { type: integer }
        start: { type: string }
YAML
