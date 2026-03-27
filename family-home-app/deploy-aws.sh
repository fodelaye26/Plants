#!/usr/bin/env bash
#
# deploy-aws.sh — Deploy the Family Home App to AWS
#
# This script provisions and deploys:
#   1. S3 bucket for asset storage (audio prompts, icons, avatars)
#   2. S3 bucket + CloudFront for the Expo web frontend
#   3. EC2 backend deployment via SSH (systemd + nginx)
#
# Prerequisites:
#   - AWS CLI v2 configured with appropriate credentials
#   - SSH access to the target EC2 instance
#   - Node.js / npx / Expo CLI installed locally (for web build)
#   - jq installed locally
#
# Usage:
#   chmod +x deploy-aws.sh
#   ./deploy-aws.sh
#
# Environment variables (override defaults):
#   AWS_REGION          — AWS region (default: us-east-1)
#   EC2_HOST            — EC2 public IP or hostname
#   EC2_USER            — SSH user (default: ubuntu)
#   EC2_KEY_FILE        — Path to SSH private key
#   GIT_REPO_URL        — Git repository URL to clone on EC2
#   DOMAIN_NAME         — (Optional) custom domain for the backend
#
set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

AWS_REGION="${AWS_REGION:-us-east-1}"
EC2_HOST="${EC2_HOST:-}"
EC2_USER="${EC2_USER:-ubuntu}"
EC2_KEY_FILE="${EC2_KEY_FILE:-}"
GIT_REPO_URL="${GIT_REPO_URL:-}"
DOMAIN_NAME="${DOMAIN_NAME:-}"

RANDOM_SUFFIX="$(head -c 4 /dev/urandom | xxd -p)"
ASSETS_BUCKET="family-home-assets-${RANDOM_SUFFIX}"
WEB_BUCKET="family-home-web-${RANDOM_SUFFIX}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# Helpers
# ============================================================================

info()  { echo -e "\n\033[1;34m==>\033[0m \033[1m$*\033[0m"; }
ok()    { echo -e "    \033[1;32m✔\033[0m $*"; }
warn()  { echo -e "    \033[1;33m⚠\033[0m $*"; }
fail()  { echo -e "    \033[1;31m✖\033[0m $*" >&2; exit 1; }

require_cmd() {
    command -v "$1" &>/dev/null || fail "'$1' is required but not installed."
}

# ============================================================================
# Preflight checks
# ============================================================================

info "Running preflight checks"
require_cmd aws
require_cmd jq
require_cmd ssh

aws sts get-caller-identity &>/dev/null || fail "AWS CLI is not configured. Run 'aws configure'."
ok "AWS CLI configured (region: ${AWS_REGION})"

# ============================================================================
# Step 1 — Create S3 bucket for asset storage
# ============================================================================

info "Creating S3 asset bucket: ${ASSETS_BUCKET}"

if [[ "${AWS_REGION}" == "us-east-1" ]]; then
    aws s3api create-bucket \
        --bucket "${ASSETS_BUCKET}" \
        --region "${AWS_REGION}" \
        > /dev/null
else
    aws s3api create-bucket \
        --bucket "${ASSETS_BUCKET}" \
        --region "${AWS_REGION}" \
        --create-bucket-configuration LocationConstraint="${AWS_REGION}" \
        > /dev/null
fi

# Block all public access — assets are served via presigned URLs
aws s3api put-public-access-block \
    --bucket "${ASSETS_BUCKET}" \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
    > /dev/null

ok "Asset bucket created and locked down"

# ============================================================================
# Step 2 — Create S3 bucket for web frontend with static hosting
# ============================================================================

info "Creating S3 web bucket: ${WEB_BUCKET}"

if [[ "${AWS_REGION}" == "us-east-1" ]]; then
    aws s3api create-bucket \
        --bucket "${WEB_BUCKET}" \
        --region "${AWS_REGION}" \
        > /dev/null
else
    aws s3api create-bucket \
        --bucket "${WEB_BUCKET}" \
        --region "${AWS_REGION}" \
        --create-bucket-configuration LocationConstraint="${AWS_REGION}" \
        > /dev/null
fi

# Enable static website hosting
aws s3 website "s3://${WEB_BUCKET}" \
    --index-document index.html \
    --error-document index.html

# Bucket policy for public read (CloudFront will front this)
aws s3api put-bucket-policy \
    --bucket "${WEB_BUCKET}" \
    --policy "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [{
            \"Sid\": \"PublicReadGetObject\",
            \"Effect\": \"Allow\",
            \"Principal\": \"*\",
            \"Action\": \"s3:GetObject\",
            \"Resource\": \"arn:aws:s3:::${WEB_BUCKET}/*\"
        }]
    }"

ok "Web bucket created with static website hosting enabled"

# ============================================================================
# Step 3 — Create CloudFront distribution for the web bucket
# ============================================================================

info "Creating CloudFront distribution for web bucket"

CF_ORIGIN_DOMAIN="${WEB_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
CF_CALLER_REF="family-home-$(date +%s)"

CF_RESULT=$(aws cloudfront create-distribution \
    --distribution-config "{
        \"CallerReference\": \"${CF_CALLER_REF}\",
        \"Comment\": \"Family Home App web frontend\",
        \"Enabled\": true,
        \"DefaultRootObject\": \"index.html\",
        \"Origins\": {
            \"Quantity\": 1,
            \"Items\": [{
                \"Id\": \"S3-${WEB_BUCKET}\",
                \"DomainName\": \"${CF_ORIGIN_DOMAIN}\",
                \"CustomOriginConfig\": {
                    \"HTTPPort\": 80,
                    \"HTTPSPort\": 443,
                    \"OriginProtocolPolicy\": \"http-only\"
                }
            }]
        },
        \"DefaultCacheBehavior\": {
            \"TargetOriginId\": \"S3-${WEB_BUCKET}\",
            \"ViewerProtocolPolicy\": \"redirect-to-https\",
            \"AllowedMethods\": {
                \"Quantity\": 2,
                \"Items\": [\"GET\", \"HEAD\"]
            },
            \"ForwardedValues\": {
                \"QueryString\": false,
                \"Cookies\": { \"Forward\": \"none\" }
            },
            \"MinTTL\": 0,
            \"DefaultTTL\": 86400,
            \"MaxTTL\": 31536000,
            \"Compress\": true
        },
        \"CustomErrorResponses\": {
            \"Quantity\": 1,
            \"Items\": [{
                \"ErrorCode\": 404,
                \"ResponsePagePath\": \"/index.html\",
                \"ResponseCode\": \"200\",
                \"ErrorCachingMinTTL\": 300
            }]
        },
        \"ViewerCertificate\": {
            \"CloudFrontDefaultCertificate\": true
        }
    }" 2>&1)

CF_DOMAIN=$(echo "${CF_RESULT}" | jq -r '.Distribution.DomainName // empty')
CF_ID=$(echo "${CF_RESULT}" | jq -r '.Distribution.Id // empty')

if [[ -n "${CF_DOMAIN}" ]]; then
    ok "CloudFront distribution created: https://${CF_DOMAIN}"
    ok "Distribution ID: ${CF_ID}"
else
    warn "CloudFront creation returned unexpected output — check manually"
    echo "${CF_RESULT}"
fi

# ============================================================================
# Step 4 — Deploy backend to EC2 via SSH
# ============================================================================

info "Deploying backend to EC2"

if [[ -z "${EC2_HOST}" ]]; then
    warn "EC2_HOST not set — skipping EC2 deployment."
    warn "Set EC2_HOST, EC2_KEY_FILE, and GIT_REPO_URL to enable."
else
    if [[ -z "${EC2_KEY_FILE}" ]]; then
        fail "EC2_KEY_FILE is required for SSH deployment."
    fi
    if [[ -z "${GIT_REPO_URL}" ]]; then
        fail "GIT_REPO_URL is required for EC2 deployment."
    fi

    SSH_CMD="ssh -o StrictHostKeyChecking=no -i ${EC2_KEY_FILE} ${EC2_USER}@${EC2_HOST}"

    info "Installing system dependencies on EC2"
    ${SSH_CMD} << 'REMOTE_DEPS'
        set -euo pipefail
        sudo apt-get update -qq
        sudo apt-get install -y -qq python3-venv python3-pip nginx git > /dev/null
REMOTE_DEPS
    ok "System dependencies installed"

    info "Cloning repo and installing Python dependencies"
    ${SSH_CMD} << REMOTE_APP
        set -euo pipefail

        # Clone or pull
        if [[ -d ~/family-home-app ]]; then
            cd ~/family-home-app && git pull
        else
            git clone ${GIT_REPO_URL} ~/family-home-app
        fi

        # Python virtual environment
        cd ~/family-home-app/backend
        python3 -m venv .venv
        .venv/bin/pip install --upgrade pip -q
        .venv/bin/pip install -r requirements.txt -q

        # Create .env from example if it doesn't exist
        if [[ ! -f .env ]]; then
            cp .env.example .env
            echo ""
            echo "WARNING: .env created from .env.example — update with real values!"
        fi
REMOTE_APP
    ok "Application code deployed"

    info "Configuring systemd service"
    ${SSH_CMD} << 'REMOTE_SYSTEMD'
        set -euo pipefail
        sudo cp ~/family-home-app/aws/systemd/family-home-api.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable family-home-api
        sudo systemctl restart family-home-api
REMOTE_SYSTEMD
    ok "systemd service configured and started"

    info "Configuring nginx reverse proxy"
    ${SSH_CMD} << 'REMOTE_NGINX'
        set -euo pipefail
        sudo cp ~/family-home-app/aws/nginx/family-home-api.conf /etc/nginx/sites-available/
        sudo ln -sf /etc/nginx/sites-available/family-home-api.conf /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo nginx -t
        sudo systemctl reload nginx
REMOTE_NGINX
    ok "nginx configured and reloaded"
fi

# ============================================================================
# Step 5 — Build and deploy Expo web export to S3
# ============================================================================

info "Building and deploying Expo web frontend"

if [[ -d "${SCRIPT_DIR}/frontend" ]]; then
    cd "${SCRIPT_DIR}/frontend"

    if command -v npx &>/dev/null; then
        npx expo export --platform web 2>&1 | tail -5
        ok "Expo web build complete"

        # Upload to S3
        aws s3 sync dist/ "s3://${WEB_BUCKET}/" \
            --delete \
            --cache-control "public, max-age=86400" \
            > /dev/null
        ok "Web frontend deployed to S3"

        # Invalidate CloudFront cache if distribution was created
        if [[ -n "${CF_ID:-}" ]]; then
            aws cloudfront create-invalidation \
                --distribution-id "${CF_ID}" \
                --paths "/*" \
                > /dev/null
            ok "CloudFront cache invalidated"
        fi
    else
        warn "npx not found — skipping frontend build. Install Node.js and run manually."
    fi
else
    warn "frontend/ directory not found — skipping frontend build."
fi

# ============================================================================
# Summary
# ============================================================================

info "Deployment complete!"
echo ""
echo "  Asset S3 Bucket:    ${ASSETS_BUCKET}"
echo "  Web S3 Bucket:      ${WEB_BUCKET}"
echo "  S3 Website URL:     http://${WEB_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
if [[ -n "${CF_DOMAIN:-}" ]]; then
echo "  CloudFront URL:     https://${CF_DOMAIN}"
echo "  CloudFront ID:      ${CF_ID}"
fi
if [[ -n "${EC2_HOST}" ]]; then
echo "  Backend API:        http://${EC2_HOST}"
fi
echo ""
echo "  Next steps:"
echo "    1. Update backend .env with real credentials and AWS_S3_BUCKET=${ASSETS_BUCKET}"
echo "    2. (Optional) Point a custom domain to CloudFront and configure SSL"
echo "    3. (Optional) Set up Let's Encrypt on EC2 for backend HTTPS"
echo "    4. (Optional) Configure IAM role on EC2 for S3 access (recommended over keys)"
echo ""
