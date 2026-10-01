
  # S3 remote state with native S3 locking (no DynamoDB needed, Terraform >= 1.10).
  # Values here cannot use variables - edit the bucket name to match terraform/bootstrap.
  backend "s3" {
    bucket       = "kuberay-agent-tfstate"
    key          = "kuberay-agent/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

# Credentials come from the standard AWS chain (aws configure / AWS_ACCESS_KEY_ID +
# AWS_SECRET_ACCESS_KEY env vars). Never put access keys in this file.
provider "aws" {
  region = "us-east-1"

}
