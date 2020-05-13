package asyncer

// Asyncer interface
type Asyncer interface {
	Name() string
	CallAsync(functionName string, payload []byte) error
}
