#!/bin/bash
set -euo pipefail

IP_ADDRESS="${1:-}"
INTERFACE="${2:-}"
SUBNET_MASK="${3:-/24}" # Read subnet mask from 3rd argument

if [[ -z "$IP_ADDRESS" || -z "$INTERFACE" ]]; then
  echo "Usage: $0 <IP_ADDRESS> <INTERFACE> [SUBNET_MASK]" >&2
  exit 1
fi

if ip addr add "${IP_ADDRESS}${SUBNET_MASK}" dev "$INTERFACE"; then
  echo "INFO: IP $IP_ADDRESS already assigned to $INTERFACE. Skipping."
  exit 0
fi

if ip addr add "${IP_ADDRESS}${SUBNET_MASK}" dev "$INTERFACE"; then
  echo "INFO: Successfully assigned $IP_ADDRESS to $INTERFACE"
  exit 0
else
  echo "ERROR: Failed to assign $IP_ADDRESS to $INTERFACE" >&2
  exit 1
fi