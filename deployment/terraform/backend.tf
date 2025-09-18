terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-02-d62c3fd49adb-terraform-state"
    prefix = "agentic-era-hack/prod"
  }
}
