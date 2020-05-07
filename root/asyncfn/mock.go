package asyncfn

import "log"

// MockAsyncer implements the Asyncer Interface for a mock
type MockAsyncer struct{}

// Name returns asyncer name
func (*MockAsyncer) Name() string {
	return "MOCK"
}

// Async runs an Async function using AWS Lambda
func (*MockAsyncer) Async(functionName string, payload []byte) error {
	log.Printf("CALLED ASYNC FUNCTION: %s\nPAYLOAD: %s", functionName, payload)
	return nil
}
