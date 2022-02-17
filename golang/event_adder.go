package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)


var sendbody =`{
	"description": "EVENT DESCRIPTION",
	"subsystem": "subsystem",
	"type": "content",
	"status": "ok",
	"payload": {
		"notes": "a sample note"
	}
}`

func main() {
	sender(sendbody)
}


func sender(sendbody string) {
	url := "https://timeline-go.dev.demo.co/timeline/events"
	// request body (payload)
	requestBody := strings.NewReader(`sendbody`)

	// post some data
	req, _ := http.NewRequest("POST", url, requestBody)

	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "Basic dGltZWxkomU6cEBTJHdPcmQ=")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := ioutil.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}