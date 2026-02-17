 # Configuration
 $PROJECT_ID = "cloudarchitect-pca"
 $REGION = "us-central1"
 $REPO_NAME = "genai-terraform"
 $SERVICE_NAME = "genai-terraform-app"
 $VERSION = "v1.0.0"

 # Build and push
 Write-Host "Building image..." -ForegroundColor Green
 docker build -t $SERVICE_NAME .

 $IMAGE_NAME = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"
 docker tag $SERVICE_NAME ${IMAGE_NAME}:${VERSION}
 docker tag $SERVICE_NAME ${IMAGE_NAME}:latest

 Write-Host "Pushing to Artifact Registry..." -ForegroundColor Green
 docker push ${IMAGE_NAME}:${VERSION}
 docker push ${IMAGE_NAME}:latest

 Write-Host "Deploying to Cloud Run..." -ForegroundColor Green
 gcloud run deploy $SERVICE_NAME `
   --image=${IMAGE_NAME}:${VERSION} `
   --platform=managed `
   --region=$REGION `
   --allow-unauthenticated `
   --port=8501 `
   --memory=2Gi `
   --cpu=2 `
   --set-secrets=GOOGLE_API_KEY=google-api-key:latest

 $SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'
 Write-Host "`nDeployment complete! Access your app at: $SERVICE_URL" -ForegroundColor Cyan