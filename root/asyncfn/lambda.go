package asyncfn

import (
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/lambda"
)

// InvokeAWSLambda isolates lambda logic. Move to an interface later if necessary
func InvokeAWSLambda(functionName string, payload []byte) error {

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
