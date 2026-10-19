#!/usr/bin/env bash

# Resume the Cloud SDK installation already downloaded by the BITS installer.

# No sudo, additional download of the SDK archive, or cluster changes.

set -euo pipefail


bits_sdk_dir="$HOME/.local/bits-gcloud/google-cloud-sdk"

if [ ! -f "$bits_sdk_dir/install.sh" ]; then

  printf 'Cloud SDK installer not found: %s/install.sh\n' "$bits_sdk_dir" >&2

  printf 'This script resumes the previously extracted BITS installation.\n' >&2

  exit 1

fi


bash "$bits_sdk_dir/install.sh" \

  --quiet \

  --path-update=false \

  --command-completion=false \

  --usage-reporting=false


export PATH="$bits_sdk_dir/bin:$PATH"

gcloud components install kubectl gke-gcloud-auth-plugin --quiet


gcloud version

kubectl version --client

gke-gcloud-auth-plugin --version


printf '\nInstallation complete. Run these commands in your terminal:\n\n'

cat <<'NEXT_STEPS'

export PATH="$HOME/.local/bits-gcloud/google-cloud-sdk/bin:$PATH"

gcloud auth login --no-launch-browser

gcloud container clusters get-credentials heart-disease-gke --region=asia-south1 --project=heart-disease-mlops-512012

kubectl -n heart-disease get pods,svc,ingress,hpa

NEXT_STEPS

