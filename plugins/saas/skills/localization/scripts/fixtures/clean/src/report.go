package report

import "golang.org/x/text/message"

func Summary(p *message.Printer, n int) string {
	return p.Sprintf("servers_checked", n)
}
