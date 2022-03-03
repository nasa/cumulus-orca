## Local Variables
locals {
  tags = merge(var.tags, { Deployment = var.prefix })
}


## Referenced Modules - Workflows
module "orca_internal_reocnciliation_workflow" {
  source = "https://github.com/nasa/cumulus/releases/download/v10.0.0/terraform-aws-cumulus-workflow.zip"
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  prefix          = var.prefix
  name            = "OrcaInternalReconciliationWorkflow"
  workflow_config = var.workflow_config
  system_bucket   = var.system_bucket
  tags            = local.tags

  state_machine_definition = templatefile(
    "${path.module}/orca_internal_reconciliation_workflow.asl.json",
    {
      orca_lambda_get_current_archive_list_arn : var.orca_lambda_get_current_archive_list_arn,
      orca_lambda_perform_orca_reconcile_arn : var.orca_lambda_perform_orca_reconcile_arn,
      orca_sqs_internal_report_queue_id: var.orca_sqs_internal_report_queue_id
    }
  )
}