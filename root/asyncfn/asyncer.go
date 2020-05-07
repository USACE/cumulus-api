package asyncfn

import (
	"log"

	"api/root/appconfig"
)

// Asyncer Interface avoids hard-coding AWS Lambda runtime everywhere in the app
// Allows theoretical implementation of other ASYNC/Serverless platforms
// if necessary in the future
type Asyncer interface {
	Async(functionName string, payload []byte) error
	Name() string
}

// GetAsyncer returns implementation of Async based on environment variables
func getAsyncer() Asyncer {

	cfg := appconfig.AppConfig()

	// AWS Lambda
	if cfg.LambdaContext {
		return &LambdaAsyncer{}
	}
	// Mock
	return &MockAsyncer{}
}

// CallAsync runs an async function using the
func CallAsync(functionName string, payload []byte) error {
	a := getAsyncer()
	log.Printf("CALL ASYNC WITH ENVIRONMENT: %s", a.Name())
	return a.Async(functionName, payload)
}
