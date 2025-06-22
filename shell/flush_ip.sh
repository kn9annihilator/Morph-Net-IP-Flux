#!/bin/bash

# -------------------------------------------------------------------
# Script: flush_ip.sh
# Description: Safely removes an IP address from a specified interface.
# Usage: ./flush_ip.sh <IP_ADDRESS> <INTERFACE>
# -------------------------------------------------------------------

set -euo pipefail

IP_ADDRESS="${1:-}"
INTERFACE="${2:-}"
LOG_FILE="$(dirname "$0")/../logs/rotation.log"

# ------------------ Logging Function ------------------
log() {
  local LEVEL="$1"
  local MESSAGE="$2"
  echo "$(date '+%Y-%m-%d %H:%M:%S') - ${LEVEL} - ${MESSAGE}" >> "$LOG_FILE"
}

# ------------------ Validate Inputs ------------------
if [[ -z "$IP_ADDRESS" || -z "$INTERFACE" ]]; then
  log "ERROR" "Usage: $0 <IP_ADDRESS> <INTERFACE>"
  exit 1
fi

# ------------------ Check if IP Exists on Interface ------------------
if ip addr show "$INTERFACE" | grep -q "$IP_ADDRESS"; then
  # Attempt to remove IP
  if sudo ip addr del "$IP_ADDRESS" dev "$INTERFACE"; then
    log "INFO" "Successfully flushed $IP_ADDRESS from $INTERFACE"
    exit 0
  else
    log "ERROR" "Failed to flush $IP_ADDRESS from $INTERFACE"
    exit 1
  fi
else
  log "INFO" "IP $IP_ADDRESS not found on $INTERFACE. No action taken."
  exit 0
fi
