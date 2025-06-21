#!/bin/bash

# -------------------------------------------------------------------
# Script: assign_ip.sh
# Description: Assigns an IP address to a given network interface.
# Usage: ./assign_ip.sh <IP_ADDRESS> <INTERFACE>
# -------------------------------------------------------------------

set -euo pipefail

IP_ADDRESS="${1:-}"
INTERFACE="${2:-}"
SUBNET_MASK="/24"  # Default subnet mask
LOG_FILE="$(dirname "$0")/../logs/rotation.log"

# ------------------ Helper: Log to file ------------------
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

# ------------------ Check if IP already exists ------------------
if ip addr show "$INTERFACE" | grep -q "$IP_ADDRESS"; then
  log "INFO" "IP $IP_ADDRESS already assigned to $INTERFACE. Skipping."
  exit 0
fi

# ------------------ Assign IP ------------------
if sudo ip addr add "${IP_ADDRESS}${SUBNET_MASK}" dev "$INTERFACE"; then
  log "INFO" "Successfully assigned $IP_ADDRESS to $INTERFACE"
  exit 0
else
  log "ERROR" "Failed to assign $IP_ADDRESS to $INTERFACE"
  exit 1
fi
