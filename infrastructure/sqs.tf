# SQS 이벤트 큐 - Kafka 대체 (비용 절감: MSK ~$180/월 → SQS ~$5/월)

resource "aws_sqs_queue" "events" {
  name                       = "${var.project_name}-events"
  delay_seconds              = 0          # 메시지 즉시 수신 가능
  max_message_size           = 262144     # 256KB (SQS 최대)
  message_retention_seconds  = 1209600    # 14일 보관
  receive_wait_time_seconds  = 10         # Long Polling (빈 응답 줄여 비용 절감)
  visibility_timeout_seconds = 60         # 처리 중 다른 소비자에게 숨김 (재처리 방지)

  # 서버 측 암호화 활성화
  sqs_managed_sse_enabled = true

  # 처리 실패 시 DLQ로 이동 (3회 실패 후)
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.events_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.project_name}-events"
  }
}

# Dead Letter Queue - 처리 실패 메시지 격리
# DLQ에 메시지가 쌓이면 앱 버그 또는 다운스트림 장애 의심
resource "aws_sqs_queue" "events_dlq" {
  name                       = "${var.project_name}-events-dlq"
  message_retention_seconds  = 1209600  # 14일 (분석/재처리 여유 기간)
  sqs_managed_sse_enabled    = true

  tags = {
    Name = "${var.project_name}-events-dlq"
  }
}

# DLQ 알람 - 메시지 발생 시 즉시 알림 (threshold=0)
# DLQ에 메시지가 있다는 것은 처리 실패를 의미하므로 즉시 확인 필요
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "${var.project_name}-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300      # 5분마다 체크
  statistic           = "Sum"
  threshold           = 0        # 1개라도 있으면 알림
  alarm_description   = "Alert when messages appear in the dead letter queue"

  dimensions = {
    QueueName = aws_sqs_queue.events_dlq.name
  }

  tags = {
    Name = "${var.project_name}-dlq-alarm"
  }
}
