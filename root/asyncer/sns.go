package asyncer

import (
	"log"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/sns"

	"fmt"
)

// SNSAsyncer implements the Asyncer Interface for SNS Messages
type SNSAsyncer struct {
	Topic string
}

// Name returns name of Asyncer
func (a SNSAsyncer) Name() string {
	return "AWS SNS"
}

// CallAsync implements Asyncer interface for AWS Lambda
func (a SNSAsyncer) CallAsync(functionName string, payload []byte) error {

	topic := a.Topic

	msg := string(payload)
	log.Printf("Async Payload: %s", msg)

	if msg == "" {
		log.Panic("Missing topic or payload!")
	}

	// Initialize a session that the SDK will use to load
	// credentials from the shared credentials file. (~/.aws/credentials).
	sess := session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	svc := sns.New(sess)

	result, err := svc.Publish(&sns.PublishInput{
		Message:  &msg,
		TopicArn: &topic,
	})
	if err != nil {
		fmt.Println(err.Error())
		return err
	}
	log.Printf(*result.MessageId)

	return nil
}
