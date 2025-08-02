#!/bin/bash
set -euo pipefail

IP_ADDRESS="${1:-}"
INTERFACE="${2:-}"
SUBNET_MASK="${3:-/24}" # Read subnet mask from 3rd argument

if [[ -z "$IP_ADDRESS" || -z "$INTERFACE" ]]; then
  echo "Usage: $0 <IP_ADDRESS> <INTERFACE> [SUBNET_MASK]" >&2
  exit 1
fi

# We grep for the IP without the mask, but crucially, delete with it.
if ip addr show "$INTERFACE" | grep -q "$IP_ADDRESS"; then
  if ip addr del "${IP_ADDRESS}${SUBNET_MASK}" dev "$INTERFACE"; then
    echo "INFO: Successfully flushed $IP_ADDRESS from $INTERFACE"
    exit 0
  else
    echo "ERROR: Failed to flush $IP_ADDRESS from $INTERFACE" >&2
    exit 1
  fi
else
  echo "INFO: IP $IP_ADDRESS not found on $INTERFACE. No action taken."
  exit 0
fi