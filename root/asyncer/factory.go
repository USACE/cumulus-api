package asyncer

import "errors"

// Config holds configuration information to build an Asyncer
type Config struct {
	Engine string
	Topic  string
}

// NewAsyncer returns a concrete asyncer
func NewAsyncer(cfg Config) (Asyncer, error) {
	switch cfg.Engine {
	case "AWSLAMBDA":
		return LambdaAsyncer{}, nil
	case "AWSSNS":
		if cfg.Topic == "" {
			return nil, errors.New(
				"Engine 'AWSSNS' requires a topic",
			)
		}
		return SNSAsyncer{Topic: cfg.Topic}, nil
	default:
		return MockAsyncer{}, nil
	}
}
