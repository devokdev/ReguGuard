#!/usr/bin/env bash
# ReguGuard Google Cloud Run Deployment Script
# PRD §12, §14 Step 13 (Criterion 11)

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"reguguard-agentic-ai"}
REGION=${GCP_REGION:-"asia-south1"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/reguguard:latest"
SERVICE_NAME="reguguard-app"

echo "Building ReguGuard container image..."
gcloud builds submit --tag ${IMAGE_NAME} .

echo "Deploying to Google Cloud Run in ${REGION}..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars="GROQ_API_KEY=${GROQ_API_KEY}"

echo "Deployment successful! Service URL:"
gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)'

