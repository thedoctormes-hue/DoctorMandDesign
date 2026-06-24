#!/bin/bash
# publish_to_yandex.sh - Upload PDF to Yandex Disk and notify via Telegram
#
# Requires:
#   - yandex.sh (from LabDoctorM/projects/DoctorM_and_Ai/bin/yandex.sh)
#   - TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables
#
# Usage:
#   ./scripts/publish_to_yandex.sh <pdf_file> [message]
#
# Example:
#   ./scripts/publish_to_yandex.sh output/poliscop_ru.pdf "New release"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
YANDEX_SH="/root/LabDoctorM/projects/DoctorM_and_Ai/bin/yandex.sh"

if [[ ! -x "$YANDEX_SH" ]]; then
  echo "Error: yandex.sh not found or not executable at $YANDEX_SH" >&2
  exit 1
fi

PDF_FILE="${1:-}"
if [[ -z "$PDF_FILE" || ! -f "$PDF_FILE" ]]; then
  echo "Usage: $0 <pdf_file> [message]" >&2
  exit 1
fi

MESSAGE="${2:-New PDF generated}"

# Upload to Yandex Disk
REMOTE_PATH="/DoctorMandDesign/releases/$(basename "$PDF_FILE")"
echo "Uploading $PDF_FILE to Yandex Disk at $REMOTE_PATH..."
UPLOAD_OUTPUT="$("$YANDEX_SH" put "$PDF_FILE" "$REMOTE_PATH" 2>&1)"
if [[ $? -ne 0 ]]; then
  echo "Failed to upload to Yandex Disk:" >&2
  echo "$UPLOAD_OUTPUT" >&2
  exit 1
fi

# Get public link
echo "Getting public link..."
PUBLIC_LINK="$("$YANDEX_SH" pub "$REMOTE_PATH" 2>&1)"
if [[ $? -ne 0 ]]; then
  echo "Failed to get public link:" >&2
  echo "$PUBLIC_LINK" >&2
  exit 1
fi

# Extract URL (assuming yandex.sh outputs just the URL)
PUBLIC_LINK=$(echo "$PUBLIC_LINK" | tr -d '\n\r')
if [[ -z "$PUBLIC_LINK" ]]; then
  echo "Empty public link received" >&2
  exit 1
fi

echo "Public link: $PUBLIC_LINK"

# Send Telegram notification
if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  TEXT="*DoctorMandDesign* 
$MESSAGE
File: $(basename "$PDF_FILE")
Download: $PUBLIC_LINK"
  
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="$TELEGRAM_CHAT_ID" \
    -d text="$TEXT" \
    -d parse_mode="Markdown" >/dev/null
  
  echo "Telegram notification sent."
else
  echo "Warning: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set, skipping Telegram notification."
fi

echo "Done."