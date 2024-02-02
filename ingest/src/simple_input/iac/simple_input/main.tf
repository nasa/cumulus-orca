## Some of these may be more common/global settings we could use at a top level for permissions
resource "aws_security_group" "allow_tls" {
  name        = "${var.prefix}-imple-input-allow-tls"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = var.vpc_id

  tags = var.tags
}

data "aws_iam_policy_document" "lambda_base" {
  statement {
    sid = "${var.prefix}LambdaBase"
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_ec2_perms" {
  statement {
    sid = "${var.prefix}LambdaEc2Perms"
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
    resources = ["*"] # Don't like * here but not sure what I would put
  }
}

data "aws_iam_policy_document" "lambda_log_perms" {
  statement {
    sid = "${var.prefix}LambdaLogPerm"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:FilterLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

data "aws_iam_policy_document" "combined" {
  source_policy_documents = [
    data.aws_iam_policy_document.lambda_ec2_perms.json,
    data.aws_iam_policy_document.lambda_log_perms.json
  ]
}

resource "aws_iam_role" "lambda_simple_input" {
  name = "${var.prefix}-simple-input-role"
  description = "simple-input lambda policy"
  assume_role_policy = data.aws_iam_policy_document.lambda_base.json
  tags = var.tags
}

resource "aws_iam_policy" "lambda_simple_input" {
  name        = "${var.prefix}-simple-input-policy"
  description = "Policy for simple-input lambda"
  policy      = data.aws_iam_policy_document.combined.json
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "simple_input_attach" {
  role       = aws_iam_role.lambda_simple_input.name
  policy_arn = aws_iam_policy.lambda_simple_input.arn
}


## Creating Lambda layers here, some of these maylive at a higher level 
## so they could be used by multiple lambdas
resource "aws_lambda_layer_version" "lambda_layer_powertools" {
  layer_name = "${var.prefix}OrcaAWSLambdaPowerTools"
  description = "Lambda layer containing the python libraries for AWS Lambda Power Tools"
  compatible_architectures = ["arm64"]
  filename = "${path.module}/aws-lambda-powertools.zip"
  source_code_hash = base64sha256("${path.module}/aws-lambda-powertools.zip")
}


resource "aws_lambda_layer_version" "lambda_layer_pydantic" {
  layer_name = "${var.prefix}OrcaPydantic"
  description = "Lambda layer containing the python libraries for Pydantic and Pydantic-Settings"
  compatible_architectures = ["arm64"]
  filename = "${path.module}/pydantic.zip"
  source_code_hash = base64sha256("${path.module}/pydantic.zip")
}


## Lambda function specific
resource "aws_lambda_function" "simple_input" {
  function_name = "${var.prefix}-simple-input"
  description   = "Simple toy lambda to provide guidance on observability and rearchitecture of ORCA."
  handler       = "simple_input.adapter.lambda_handler"
  architectures = ["arm64"]
  runtime       = "python3.11"
  memory_size   = 128
  timeout       = 30
  role          = aws_iam_role.lambda_simple_input.arn

  package_type  = "Zip"
  filename      = "${path.module}/simple_input.zip"
  source_code_hash = base64sha256("${path.module}/simple_input.zip")
  layers = [
    aws_lambda_layer_version.lambda_layer_powertools.arn,
    aws_lambda_layer_version.lambda_layer_pydantic.arn
  ]
  publish          = true

  logging_config {
    application_log_level = var.log_level
    system_log_level = var.log_level
    log_format = "JSON"
    log_group = var.log_group
  }

  tags = var.tags

  environment {
    variables = {
        DEFAULT_STORAGE_CLASS = "GLACIER"
        DEFAULT_ORCA_BUCKET = "orca-primary-archive"
        DEFAULT_MULTIPART_CHUNKSIZE_MB = 256
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.allow_tls.id]
  }
}


## Integration with the APIGW would be nice here
