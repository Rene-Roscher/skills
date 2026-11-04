package report

import (
	"fmt"
	"net/http"
)

func Summary(n int) string {
	return fmt.Sprintf("%d servers checked", n)
}

func Handle(w http.ResponseWriter, err error) {
	http.Error(w, err.Error(), http.StatusInternalServerError)
}
