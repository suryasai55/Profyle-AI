import time
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class CloudWatchLogHandler(logging.Handler):
    """
    Custom Python logging Handler that streams formatting records 
    directly to AWS CloudWatch logs via Boto3.
    """
    def __init__(self, log_group, log_stream, config):
        super().__init__()
        self.log_group = log_group
        self.log_stream = log_stream
        self.config = config
        self.sequence_token = None
        self.client = None
        self.enabled = False
        
        # Initialize boto3 CloudWatch logs client
        try:
            # Reuses S3 key configurations or falls back to EC2 IAM Role
            self.client = boto3.client(
                'logs',
                aws_access_key_id=config.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=config.get('AWS_SECRET_ACCESS_KEY'),
                region_name=config.get('AWS_REGION', 'us-east-1')
            )
            
            # Ensure Log Group and Log Stream exist
            self._init_log_destinations()
            self.enabled = True
        except (NoCredentialsError, ClientError) as e:
            # Quietly disable handler during local development when AWS credentials are absent
            print(f"CloudWatch logger disabled: {str(e)}")
        except Exception as e:
            print(f"Error initializing CloudWatch logger: {str(e)}")

    def _init_log_destinations(self):
        """Creates CloudWatch log group and log stream if they do not exist."""
        # 1. Create Log Group
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
            
        # 2. Create Log Stream
        try:
            self.client.create_log_stream(logGroupName=self.log_group, logStreamName=self.log_stream)
        except self.client.exceptions.ResourceAlreadyExistsException:
            # If stream exists, fetch the sequence token
            response = self.client.describe_log_streams(
                logGroupName=self.log_group,
                logStreamNamePrefix=self.log_stream
            )
            streams = response.get('logStreams', [])
            if streams:
                self.sequence_token = streams[0].get('uploadSequenceToken')

    def emit(self, record):
        """Streams log records directly to CloudWatch logs."""
        if not self.enabled or not self.client:
            return
            
        try:
            log_message = self.format(record)
            timestamp = int(round(time.time() * 1000))
            
            log_event = {
                'timestamp': timestamp,
                'message': log_message
            }
            
            kwargs = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream,
                'logEvents': [log_event]
            }
            
            if self.sequence_token:
                kwargs['sequenceToken'] = self.sequence_token
                
            response = self.client.put_log_events(**kwargs)
            self.sequence_token = response.get('nextSequenceToken')
            
        except ClientError as e:
            # If sequence token mismatch occurs, resolve it dynamically
            if e.response['Error']['Code'] in ('InvalidSequenceTokenException', 'DataAlreadyAcceptedException'):
                self.sequence_token = e.response['Error'].get('expectedSequenceToken')
                # Retry once
                try:
                    kwargs['sequenceToken'] = self.sequence_token
                    response = self.client.put_log_events(**kwargs)
                    self.sequence_token = response.get('nextSequenceToken')
                except:
                    pass
            else:
                pass
        except Exception:
            # Safeguard so logging failures never crash the main application thread
            pass
