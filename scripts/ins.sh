#!/usr/bin/env bash

# Run on BITS after Google Cloud CLI installation.

# Installs kubectl and the GKE authentication plugin; does not change the cluster.

set -euo pipefail


bits_sdk_bin="$HOME/.local/bits-gcloud/google-cloud-sdk/bin"

if [ -x "$bits_sdk_bin/gcloud" ]; then

  export PATH="$bits_sdk_bin:$PATH"

fi


if ! command -v gcloud >/dev/null 2>&1; then

  printf 'gcloud is not available. Complete the gcloud installation first.\n' >&2

  exit 1

fi


printf 'Installing kubectl and the GKE authentication plugin...\n'

if ! gcloud components install kubectl gke-gcloud-auth-plugin --quiet; then

  printf '\nInstallation failed. If component management is disabled by the lab, ask its administrator to provide kubectl and gke-gcloud-auth-plugin.\n' >&2

  exit 1

fi


kubectl version --client

gke-gcloud-auth-plugin --version


printf '\nInstallation complete. To connect, run these commands in your terminal:\n\n'

if [ -x "$bits_sdk_bin/gcloud" ]; then

  printf 'export PATH="$HOME/.local/bits-gcloud/google-cloud-sdk/bin:$PATH"\n'

fi

cat <<'NEXT_STEPS'

gcloud auth login --no-launch-browser

gcloud container clusters get-credentials heart-disease-gke --region=asia-south1 --project=heart-disease-mlops-512012

kubectl -n heart-disease get pods,svc,ingress,hpa

NEXT_STEPS


