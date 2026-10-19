#!/usr/bin/env bash
# Read-only checks. No installation or cloud changes.
set -u
printf 'BITS Rocky Linux preflight\n'
if [ -f /etc/os-release ]; then cat /etc/os-release; fi
printf '\nProject directory: %s\n' "$PWD"
for tool_name in python3.11 docker git curl unzip gcloud kubectl gke-gcloud-auth-plugin; do
  if command -v "$tool_name" >/dev/null 2>&1; then
    printf 'FOUND   %s: %s\n' "$tool_name" "$(command -v "$tool_name")"
  else
    printf 'MISSING %s\n' "$tool_name"
  fi
done
if command -v docker >/dev/null 2>&1; then
  docker version || printf 'ACTION: Docker daemon access needs attention.\n'
  docker compose version || printf 'ACTION: Docker Compose plugin needs attention.\n'
fi
printf '\nUse GKE_ON_ROCKY.md for gcloud/kubectl/auth-plugin setup.\n'
printf 'Use BITS_ROCKY_LINUX_FINAL_RUN_README.md for execution and screenshots.\n'
