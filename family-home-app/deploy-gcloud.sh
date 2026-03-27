#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Family Home App — Google Cloud Run deployment script
# ============================================================
#
# Prerequisites:
#   1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
#   2. Run: gcloud auth login
#   3. Create a GCP project and set it:
#      gcloud projects create family-home-app --name="Family Home App"
#      gcloud config set project family-home-app
#   4. Enable required APIs:
#      gcloud services enable run.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com
#   5. Set your env vars below
#
# Usage:
#   chmod +x deploy-gcloud.sh
#   ./deploy-gcloud.sh
# ============================================================

# --- Configuration (edit these) ---
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="family-home-api"
NOTION_API_KEY="${NOTION_API_KEY:?Set NOTION_API_KEY env var}"
NOTION_TASKS_DB_ID="${NOTION_TASKS_DB_ID:-bfe5382f554c4e8492c1dd1e99a9a4cb}"
NOTION_CHORES_DB_ID="${NOTION_CHORES_DB_ID:-27e93b58f22f8158b024ebaf7354a277}"

echo "==> Deploying Family Home API to Google Cloud Run"
echo "    Project:  $PROJECT_ID"
echo "    Region:   $REGION"
echo "    Service:  $SERVICE_NAME"
echo ""

# --- Step 1: Deploy to Cloud Run (source-based, uses Dockerfile) ---
echo "==> Building and deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --source ./family-home-app/backend \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "\
NOTION_API_KEY=$NOTION_API_KEY,\
NOTION_TASKS_DB_ID=$NOTION_TASKS_DB_ID,\
NOTION_CHORES_DB_ID=$NOTION_CHORES_DB_ID,\
DATABASE_URL=sqlite:///./family_home.db,\
APP_ENV=production"

# --- Step 2: Get the service URL ---
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --format "value(status.url)")

echo ""
echo "============================================================"
echo "  Deployment complete!"
echo ""
echo "  API URL:    $SERVICE_URL"
echo "  Docs:       $SERVICE_URL/docs"
echo "  Health:     $SERVICE_URL/health"
echo ""
echo "  Next steps:"
echo "  1. Update your frontend EXPO_PUBLIC_API_URL:"
echo "     EXPO_PUBLIC_API_URL=${SERVICE_URL}/api"
echo ""
echo "  2. For persistent storage, add Cloud SQL:"
echo "     gcloud sql instances create family-home-db \\"
echo "       --database-version=POSTGRES_15 \\"
echo "       --tier=db-f1-micro \\"
echo "       --region=$REGION"
echo ""
echo "     Then update DATABASE_URL env var on Cloud Run."
echo "============================================================"
