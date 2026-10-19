#!/usr/bin/env bash
# Run on the BITS host only. User-directory installation; no sudo.
set -euo pipefail
if [ "$(uname -s)" != Linux ] || [ "$(uname -m)" != x86_64 ]; then
  printf 'This installer supports Linux x86_64. Use the official Google Cloud CLI installer for your architecture.\n' >&2
  exit 1
fi
command -v curl >/dev/null
command -v tar >/dev/null
if command -v gcloud >/dev/null 2>&1; then
  printf 'Existing gcloud found: %s\n' "$(command -v gcloud)"
  printf 'Use GKE_ON_ROCKY.md to check/install components. Existing installation was not modified.\n'
  exit 0
fi
bits_sdk_root="$HOME/.local/bits-gcloud"
if [ -e "$bits_sdk_root" ]; then
  printf 'Directory already exists: %s. Inspect it before rerunning; nothing overwritten.\n' "$bits_sdk_root" >&2
  exit 1
fi
bits_download_dir=$(mktemp -d)
trap 'rm -rf -- "$bits_download_dir"' EXIT
curl --fail --location --retry 2 \
  https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz \
  -o "$bits_download_dir/google-cloud-cli.tar.gz"
mkdir -p "$bits_sdk_root"
tar -xzf "$bits_download_dir/google-cloud-cli.tar.gz" -C "$bits_sdk_root"
"$bits_sdk_root/google-cloud-sdk/install.sh" \
  --quiet --path-update=false --command-completion=false --usage-reporting-enabled=false
export PATH="$bits_sdk_root/google-cloud-sdk/bin:$PATH"
gcloud components install kubectl gke-gcloud-auth-plugin --quiet
printf '\nInstallation complete. Run in EVERY terminal that needs these tools:\n'
printf 'export PATH="$HOME/.local/bits-gcloud/google-cloud-sdk/bin:$PATH"\n'
printf '\nThen follow GKE_ON_ROCKY.md.\n'
