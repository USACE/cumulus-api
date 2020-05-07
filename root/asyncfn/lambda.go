package asyncfn

import (
	"log"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/lambda"
)

// LambdaAsyncer implements the Asyncer Interface for AWS Lambda
type LambdaAsyncer struct{}

// Name returns name of Asyncer
func (*LambdaAsyncer) Name() string {
	return "AWS LAMBDA"
}

// Async runs an Async function using AWS Lambda
func (*LambdaAsyncer) Async(functionName string, payload []byte) error {

	log.Printf("CALLED ASYNC FUNCTION: %s\nPAYLOAD: %s", functionName, payload)

	// session
	sess := session.Must(session.NewSession())
	// client
	client := lambda.New(sess, &aws.Config{Region: aws.String("us-east-1")})

	if _, err := client.Invoke(
		&lambda.InvokeInput{FunctionName: aws.String(functionName), Payload: payload},
	); err != nil {
		return err
	}

	return nil
}
