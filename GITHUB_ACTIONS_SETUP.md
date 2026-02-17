# GitHub Actions CI/CD Setup Guide

This guide will help you set up automated deployment to Google Cloud Run using GitHub Actions.

**Recommended Approach:** Method 2 (Workload Identity Federation) - More secure, no long-lived credentials

## Quick Setup Summary (Method 2)

For those who want a quick overview, here are the main steps:

1. Create Workload Identity Pool and Provider (OIDC with GitHub)
2. Create `github-actions` service account (for CI/CD operations)
3. Bind GitHub repository to service account via workload identity
4. Create Artifact Registry repository
5. Create `cloud-run-sa` service account (for runtime with minimal permissions)
6. Grant Secret Manager access to `cloud-run-sa`
7. Add `GCP_PROJECT_NUMBER` to GitHub Secrets
8. Deploy via GitHub Actions

---

## Method 1: Using Service Account Key (Simpler)

### Step 1: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployment" \
  --project=cloudarchitect-pca

# Grant necessary permissions
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
```

### Step 2: Create and Download Service Account Key

```bash
# Create key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@cloudarchitect-pca.iam.gserviceaccount.com

# Display the key content (copy this)
cat github-actions-key.json
```

### Step 3: Add Secret to GitHub Repository

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GCP_SA_KEY`
5. Value: Paste the entire JSON content from `github-actions-key.json`
6. Click **Add secret**

### Step 4: Create Secret in Google Secret Manager

```bash
# If not already created, create the Google API key secret
echo "your_google_gemini_api_key" | gcloud secrets create google-api-key \
  --data-file=- \
  --project=cloudarchitect-pca

# Grant Cloud Run service account access to the secret
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=cloudarchitect-pca
```

### Step 5: Use the Workflow

The workflow file `.github/workflows/deploy.yml` is ready to use. It will automatically:
- Trigger on push to `main` or `master` branch
- Build Docker image
- Push to Artifact Registry
- Deploy to Cloud Run

---

## Method 2: Using Workload Identity Federation (More Secure - Recommended for Production)

### Step 1: Create Workload Identity Pool

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe cloudarchitect-pca --format="value(projectNumber)")
echo "Project Number: $PROJECT_NUMBER"

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
  --attribute-condition="assertion.repository_owner=='raghavendrajupudi-ai'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# OPTIONAL: Add attribute condition to restrict to specific GitHub user/org
# Only use if you want to limit access to repositories from a specific owner
# --attribute-condition="assertion.repository_owner=='YOUR_GITHUB_USERNAME'"
```

### Step 2: Create Service Account and Grant Permissions

```bash
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
```

### Step 3: Allow GitHub Actions to Impersonate Service Account

```bash
# IMPORTANT: Get project number first (from Step 1)
PROJECT_NUMBER=$(gcloud projects describe cloudarchitect-pca --format="value(projectNumber)")
echo "Project Number: $PROJECT_NUMBER"

# Verify PROJECT_NUMBER is set (should be a numeric value)
if [ -z "$PROJECT_NUMBER" ]; then
  echo "ERROR: PROJECT_NUMBER is not set. Run the command above first."
  exit 1
fi

# Replace YOUR_GITHUB_ORG and YOUR_GITHUB_REPO with your values
# Example: raghavendrajupudi-ai/genai-with-terraform
REPO="YOUR_GITHUB_ORG/YOUR_GITHUB_REPO"

# Add workload identity binding
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@cloudarchitect-pca.iam.gserviceaccount.com \
  --project=cloudarchitect-pca \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO"
```

### Step 4: Create Artifact Registry Repository

```bash
# Create Docker repository in Artifact Registry
gcloud artifacts repositories create genai-terraform \
  --repository-format=docker \
  --location=us-central1 \
  --project=cloudarchitect-pca \
  --description="Docker repository for GenAI Terraform app"

# Grant github-actions service account write access
gcloud artifacts repositories add-iam-policy-binding genai-terraform \
  --location=us-central1 \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer" \
  --project=cloudarchitect-pca
```

### Step 5: Create Dedicated Cloud Run Service Account (Best Practice)

```bash
# Create a dedicated service account for Cloud Run (better security than default compute account)
gcloud iam service-accounts create cloud-run-sa \
  --display-name="Cloud Run Service Account" \
  --project=cloudarchitect-pca

# Grant Secret Manager access (for accessing google-api-key)
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:cloud-run-sa@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=cloudarchitect-pca

# Grant the github-actions service account permission to act as the Cloud Run service account
gcloud iam service-accounts add-iam-policy-binding cloud-run-sa@cloudarchitect-pca.iam.gserviceaccount.com \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --project=cloudarchitect-pca

# Verify the setup
gcloud iam service-accounts describe cloud-run-sa@cloudarchitect-pca.iam.gserviceaccount.com \
  --project=cloudarchitect-pca
```

**Benefits of dedicated Cloud Run service account:**
- ✅ Principle of least privilege (only Secret Manager access)
- ✅ Better isolation from default compute account
- ✅ Easier to audit and manage permissions
- ✅ More secure than using default service accounts

### Step 6: Add GitHub Secrets

1. **Get your project number:**
```bash
gcloud projects describe cloudarchitect-pca --format="value(projectNumber)"
```

2. **Add to GitHub repository:**
   - Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
   - Click **New repository secret**
   - Add the following secret:
     - **Name**: `GCP_PROJECT_NUMBER`
     - **Value**: (paste the project number from step 1)
   - Click **Add secret**

### Step 7: Verify Workflow File Configuration

Ensure your `.github/workflows/deploy.yml` has the following configuration:

```yaml
env:
  PROJECT_ID: cloudarchitect-pca
  REGION: us-central1
  REPOSITORY: genai-terraform
  SERVICE_NAME: genai-terraform-app
  WORKLOAD_IDENTITY_PROVIDER: projects/${{ secrets.GCP_PROJECT_NUMBER }}/locations/global/workloadIdentityPools/github-pool/providers/github-provider
  SERVICE_ACCOUNT: github-actions@cloudarchitect-pca.iam.gserviceaccount.com
```

And in the deploy step, verify it uses the dedicated Cloud Run service account:

```yaml
flags: |
  --port=8501
  --memory=2Gi
  --cpu=2
  --timeout=300
  --allow-unauthenticated
  --min-instances=0
  --max-instances=10
  --service-account=cloud-run-sa@cloudarchitect-pca.iam.gserviceaccount.com
  --set-secrets=GOOGLE_API_KEY=google-api-key:latest
```

---

## Workflow Features

Both workflows include:

✅ Automatic build on push to main/master  
✅ Manual trigger via GitHub Actions UI  
✅ Docker image build and push to Artifact Registry  
✅ Automatic deployment to Cloud Run  
✅ Health check verification  
✅ Image tagging with git commit SHA + latest  
✅ Auto-scaling configuration  
✅ Secure secret management  

---

## Testing the Workflow

1. **Commit and push to trigger deployment:**
```bash
git add .
git commit -m "Add GitHub Actions CI/CD pipeline"
git push origin main
```

2. **Monitor the deployment:**
   - Go to your GitHub repository
   - Click on **Actions** tab
   - Watch the workflow run

3. **Manual trigger:**
   - Go to **Actions** tab
   - Select **Deploy to Cloud Run** workflow
   - Click **Run workflow**
   - Select branch and click **Run workflow**

---

## Troubleshooting

### Common Issues

**Authentication Failed:**
```bash
# Verify service account exists
gcloud iam service-accounts list --project=cloudarchitect-pca

# Check permissions
gcloud projects get-iam-policy cloudarchitect-pca \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com"
```

**Artifact Registry Push Failed:**
```bash
# Verify repository exists
gcloud artifacts repositories describe genai-terraform \
  --location=us-central1 \
  --project=cloudarchitect-pca

# Create if needed
gcloud artifacts repositories create genai-terraform \
  --repository-format=docker \
  --location=us-central1 \
  --project=cloudarchitect-pca \
  --description="Docker repository for GenAI Terraform app"

# Grant permissions
gcloud artifacts repositories add-iam-policy-binding genai-terraform \
  --location=us-central1 \
  --member="serviceAccount:github-actions@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer" \
  --project=cloudarchitect-pca
```

**Secret Not Found or Permission Denied:**
```bash
# List secrets
gcloud secrets list --project=cloudarchitect-pca

# Create if needed
echo "your_google_gemini_api_key" | gcloud secrets create google-api-key \
  --data-file=- \
  --project=cloudarchitect-pca

# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:cloud-run-sa@cloudarchitect-pca.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=cloudarchitect-pca
```

**Workload Identity Federation Issues:**
```bash
# Verify PROJECT_NUMBER is set correctly in GitHub secrets
PROJECT_NUMBER=$(gcloud projects describe cloudarchitect-pca --format="value(projectNumber)")
echo "Project Number: $PROJECT_NUMBER"

# Check workload identity pool exists
gcloud iam workload-identity-pools describe github-pool \
  --location=global \
  --project=cloudarchitect-pca

# Check provider configuration
gcloud iam workload-identity-pools providers describe github-provider \
  --workload-identity-pool=github-pool \
  --location=global \
  --project=cloudarchitect-pca
```

---

## Security Best Practices

1. ✅ **Use Workload Identity Federation** instead of service account keys (no long-lived credentials)
2. ✅ **Use dedicated Cloud Run service account** with minimal permissions (principle of least privilege)
3. ✅ **Store sensitive values in GitHub Secrets** (never commit to repository)
4. ✅ **Use separate service accounts** for different environments (dev, staging, prod)
5. ✅ **Grant only necessary IAM roles** to each service account
6. ✅ **Enable Cloud Audit Logs** for tracking and compliance
7. ✅ **Regularly review IAM policies** and remove unused permissions
8. ✅ **Use Secret Manager** for runtime secrets instead of environment variables

**Service Accounts Summary:**
- `github-actions@cloudarchitect-pca.iam.gserviceaccount.com` - For CI/CD deployment operations
- `cloud-run-sa@cloudarchitect-pca.iam.gserviceaccount.com` - For Cloud Run runtime (minimal permissions)

---

## Environment-Specific Deployments

To deploy to different environments (dev, staging, prod), create branches and update the workflow:

```yaml
on:
  push:
    branches:
      - main        # Production
      - staging     # Staging
      - develop     # Development

env:
  SERVICE_NAME: genai-terraform-app-${{ github.ref_name }}
```

---

## Cost Optimization

Current configuration:
- **Min instances**: 0 (scales to zero when not in use)
- **Max instances**: 10
- **Memory**: 2GB per instance
- **CPU**: 2 vCPUs

Adjust based on your needs in the workflow file.
