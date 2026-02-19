# SQS Queue for Event Messaging (Kafka replacement)

resource "aws_sqs_queue" "events" {
  name                       = "${var.project_name}-events"
  delay_seconds              = 0
  max_message_size           = 262144  # 256 KB
  message_retention_seconds  = 1209600 # 14 days
  receive_wait_time_seconds  = 10      # Long polling
  visibility_timeout_seconds = 60

  # Enable server-side encryption
  sqs_managed_sse_enabled = true

  # Redrive policy for dead-letter queue
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.events_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.project_name}-events"
  }
}

# Dead Letter Queue
resource "aws_sqs_queue" "events_dlq" {
  name                       = "${var.project_name}-events-dlq"
  message_retention_seconds  = 1209600 # 14 days
  sqs_managed_sse_enabled    = true

  tags = {
    Name = "${var.project_name}-events-dlq"
  }
}

# CloudWatch Alarm for DLQ messages
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "${var.project_name}-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alert when messages appear in the dead letter queue"

  dimensions = {
    QueueName = aws_sqs_queue.events_dlq.name
  }

  tags = {
    Name = "${var.project_name}-dlq-alarm"
  }
}
