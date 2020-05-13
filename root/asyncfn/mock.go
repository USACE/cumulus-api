package asyncfn

import "log"

// MockAsyncer implements the Asyncer Interface for a mock
type MockAsyncer struct{}

// Name returns asyncer name
func (*MockAsyncer) Name() string {
	return "MOCK"
}

// Async runs an Async function using AWS Lambda
func (a *MockAsyncer) Async(functionName string, payload []byte) error {
	log.Printf(
		"ASYNC ENV: %s; FUNCTION: %s;PAYLOAD: %s",
		a.Name(),
		functionName,
		payload,
	)
	return nil
}
