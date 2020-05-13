package asyncer

import "log"

// MockAsyncer implements the Asyncer Interface for a mock
type MockAsyncer struct{}

// Name returns asyncer name
func (a MockAsyncer) Name() string {
	return "MOCK"
}

// CallAsync implements Asyncer interface for Mock
func (a MockAsyncer) CallAsync(functionName string, payload []byte) error {
	log.Printf(
		"ASYNC ENV: %s; FUNCTION: %s;PAYLOAD: %s",
		a.Name(),
		functionName,
		payload,
	)
	return nil
}
