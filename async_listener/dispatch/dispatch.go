// Package dispatch sends job payloads to the queues the Python workers consume.
//
// It replaces github.com/USACE/go-simple-asyncer, which pinned aws-sdk-go v1
// and so carried CVE-2020-8911 and CVE-2020-8912 -- neither of which was ever
// patched on the v1 line.
//
// The wire contract is deliberately unchanged: a plain SQS message whose body
// is the JSON payload. That is what async_geoprocess/worker.py and
// async_packager/packager.py read via boto3 receive_messages, so nothing on the
// consumer side has to change.
package dispatch

import (
	"context"
	"fmt"
	"log"
	"net/url"
	"path"
	"strings"
	"sync"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/sqs"
)

// Sender delivers a payload to a worker queue.
type Sender interface {
	Name() string
	Send(ctx context.Context, payload []byte) error
}

// New builds a Sender from the same ASYNC_ENGINE_* / ASYNC_ENGINE_*_TARGET
// environment contract go-simple-asyncer used, so no infrastructure config
// changes with this swap:
//
//	engine "AWSSQS", target "<queue-name>"          -> real SQS, URL resolved via GetQueueUrl
//	engine "AWSSQS", target "local/<queue-url>"     -> SQS-compatible endpoint (ElasticMQ locally)
//	anything else                                   -> logging no-op, as MockAsyncer was
//
// Engines "AWSSNS", "AWSLAMBDA" and "AMQP" existed upstream but are not
// implemented here: every ASYNC_ENGINE_* value in this repo is AWSSQS or MOCK.
// They fall through to the no-op rather than failing silently at send time, and
// New reports that clearly so a misconfiguration is visible at startup.
func New(ctx context.Context, engine, target string) (Sender, error) {
	if !strings.EqualFold(engine, "AWSSQS") {
		if engine != "" && !strings.EqualFold(engine, "MOCK") {
			log.Printf(
				"dispatch: engine %q is not implemented; falling back to a no-op sender. "+
					"Only AWSSQS performs real delivery.", engine,
			)
		}
		return noop{engine: engine, target: target}, nil
	}

	awsCfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return nil, fmt.Errorf("dispatch: loading AWS config: %w", err)
	}

	// "local/<url>" points at an SQS-compatible endpoint (ElasticMQ in
	// docker-compose). The queue URL is known up front, so no lookup is needed.
	if len(target) > 6 && strings.EqualFold(target[:6], "local/") {
		raw := target[6:]
		u, err := url.Parse(raw)
		if err != nil {
			return nil, fmt.Errorf("dispatch: parsing local target %q: %w", raw, err)
		}
		endpoint := fmt.Sprintf("%s://%s", u.Scheme, u.Host)
		_, queueName := path.Split(u.Path)
		client := sqs.NewFromConfig(awsCfg, func(o *sqs.Options) {
			o.BaseEndpoint = aws.String(endpoint)
		})
		return &sqsSender{client: client, queueURL: raw, queueName: queueName}, nil
	}

	return &sqsSender{client: sqs.NewFromConfig(awsCfg), queueName: target}, nil
}

type sqsSender struct {
	client    *sqs.Client
	queueName string

	// queueURL is known up front for local targets. For real SQS it is resolved
	// on first send and cached. Resolution is deliberately lazy so that a queue
	// which is not reachable at boot does not stop the listener from starting --
	// go-simple-asyncer resolved per message, which had the same tolerance but
	// cost an extra API call on every dispatch.
	mu       sync.Mutex
	queueURL string
}

func (s *sqsSender) Name() string { return "AWSSQS" }

func (s *sqsSender) url(ctx context.Context) (string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.queueURL != "" {
		return s.queueURL, nil
	}
	out, err := s.client.GetQueueUrl(ctx, &sqs.GetQueueUrlInput{QueueName: aws.String(s.queueName)})
	if err != nil {
		return "", fmt.Errorf("dispatch: resolving queue %q: %w", s.queueName, err)
	}
	s.queueURL = aws.ToString(out.QueueUrl)
	return s.queueURL, nil
}

func (s *sqsSender) Send(ctx context.Context, payload []byte) error {
	queueURL, err := s.url(ctx)
	if err != nil {
		return err
	}
	if _, err := s.client.SendMessage(ctx, &sqs.SendMessageInput{
		QueueUrl:    aws.String(queueURL),
		MessageBody: aws.String(string(payload)),
	}); err != nil {
		return fmt.Errorf("dispatch: sending to %q: %w", s.queueName, err)
	}
	return nil
}

type noop struct{ engine, target string }

func (n noop) Name() string { return "NOOP" }

func (n noop) Send(_ context.Context, payload []byte) error {
	log.Printf("dispatch: no-op sender (engine=%q target=%q); payload: %s", n.engine, n.target, payload)
	return nil
}
