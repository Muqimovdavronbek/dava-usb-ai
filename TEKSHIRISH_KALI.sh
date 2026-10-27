#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
printf '%s\n' 'Fayllar tekshirilyapti. Katta model tufayli bir oz kuting.'
sha256sum --check SHA256SUMS.txt
printf '\n%s\n' 'Hammasi mos. Endi bash BOSHLASH_KALI.sh buyrugini bajaring.'
