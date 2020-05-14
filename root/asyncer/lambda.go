package asyncer

import (
	"log"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/lambda"
)

// LambdaAsyncer implements the Asyncer Interface for AWS Lambda
type LambdaAsyncer struct{}

// Name returns name of Asyncer
func (a LambdaAsyncer) Name() string {
	return "AWS LAMBDA"
}

// CallAsync implements Asyncer interface for AWS Lambda
func (a LambdaAsyncer) CallAsync(functionName string, payload []byte) error {

	log.Printf(
		"ASYNC ENV: %s; FUNCTION: %s;PAYLOAD: %s",
		a.Name(),
		functionName,
		payload,
	)

	// session
	sess := session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	// client
	client := lambda.New(sess, &aws.Config{Region: aws.String("us-east-1")})

	output, err := client.Invoke(
		&lambda.InvokeInput{
			FunctionName:   aws.String(functionName),
			InvocationType: aws.String("Event"),
			Payload:        payload,
		},
	)
	if err != nil {
		log.Printf("AWS Lambda Error; %s", err.Error())
		return err
	}
	log.Print(output)
	return nil
}
