from airflow.providers.amazon.aws.hooks.sqs import SQSHook


def trigger_sqs(*args, **kwargs):

    # IF Using SQS "Local" (i.e. ElasticMQ)
    # Endpoint should be http://elasticmq:9324
    # Queue Name Should be 
    # Queue URL should be http://elasticmq:9324/queue/cumulus-packager

    QUEUE_URL = f'http://elasticmq:9324/queue/{kwargs["queue_name"]}'
    print(f'Queue URL is: {QUEUE_URL}')

    SQS = SQSHook(aws_conn_id='SQS')
    SQS.send_message(QUEUE_URL, kwargs['message'])
