resource "aws_iam_role" "restore_object_role" {
  name               = "restore_object_role"
  assume_role_policy = "${data.aws_iam_policy_document.restore_object_policy_document.json}"
}

data "aws_iam_policy_document" "restore_object_policy_document" {
  statement {
    actions   = [
      "s3:RestoreObject",
      "s3:GetObject"
    ]
    resources = [
      "arn:aws:s3:::${var.archive_bucket}",
      "arn:aws:s3:::${var.archive_bucket}/*"
    ]
  }
}
