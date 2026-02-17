#!/bin/bash

# Get project number
PROJECT_NUMBER=$(gcloud projects describe cloudarchitect-pca --format="value(projectNumber)")
echo "Project Number: $PROJECT_NUMBER"

# Verify PROJECT_NUMBER is set
if [ -z "$PROJECT_NUMBER" ]; then
  echo "ERROR: PROJECT_NUMBER is not set. Cannot continue."
  exit 1
fi

# Enable required APIs
gcloud services enable iamcredentials.googleapis.com --project=cloudarchitect-pca

# Create workload identity pool
gcloud iam workload-identity-pools create github-pool \
  --project=cloudarchitect-pca \
  --location=global \
  --display-name="GitHub Actions Pool"

# Create workload identity provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project=cloudarchitect-pca \
  --location=global \
  --workload-identity-pool=github-pool \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"


### Step 2: Create Service Account and Grant Permissions
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions" \
  --project=cloudarchitect-pca

# Grant permissions
gcloud projects add-iam-policy-binding cloudarchitect-pca \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding cloudarchitect-pca \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding cloudarchitect-pca \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding cloudarchitect-pca \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
  
### Step 3: Allow GitHub Actions to Impersonate Service Account

# Verify PROJECT_NUMBER is still set
if [ -z "$PROJECT_NUMBER" ]; then
  PROJECT_NUMBER=$(gcloud projects describe cloudarchitect-pca --format="value(projectNumber)")
  echo "Project Number: $PROJECT_NUMBER"
fi

# Replace YOUR_GITHUB_ORG and YOUR_GITHUB_REPO with your values
# Example: raghavendrajupudi-ai/genai-with-terraform
REPO="YOUR_GITHUB_ORG/YOUR_GITHUB_REPO"

echo "Using member: principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO"

gcloud iam service-accounts add-iam-policy-binding \
  github-actions@cloudarchitect-pca.iam.gserviceaccount.com \
  --project=cloudarchitect-pca \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO"  
  
  
  