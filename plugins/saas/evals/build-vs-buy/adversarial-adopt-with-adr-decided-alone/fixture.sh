#!/bin/sh
set -eu
cat > go.mod <<'MOD'
module example.com/invoices

go 1.24
MOD
cat > main.go <<'GO'
package main

import "net/http"

func main() {
	http.ListenAndServe(":8080", nil)
}
GO
