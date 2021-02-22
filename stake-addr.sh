#!/usr/bin/env bash
FULL_ADDR=$1
FULL_ADDR_HEX=$(bech32 <<< "$FULL_ADDR")
STAKE_ADDR_HEX="e1${FULL_ADDR_HEX: -56}"
STAKE_ADDR_HEX_POOLTOOL="${FULL_ADDR_HEX: -56}"
STAKE_ADDR_BECH32="$(bech32 stake <<< "$STAKE_ADDR_HEX")"
printf "%-26s %s\n" "Full Address:" "${FULL_ADDR}"
printf "%-26s %s\n" "Full Address (Hex):" "${FULL_ADDR_HEX}"
printf "%-26s %s\n" "Stake Address (Hex):" "${STAKE_ADDR_HEX}"
printf "%-26s %s\n" "Stake Address (pooltool):" "${STAKE_ADDR_HEX_POOLTOOL}"
printf "%-26s %s\n" "Stake Address (bech32):" "${STAKE_ADDR_BECH32}"
