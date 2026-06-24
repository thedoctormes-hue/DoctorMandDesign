#!/usr/bin/env bash
# setup_fonts.sh — скрипт для установки шрифтов (Inter и Oswald)
# В данной реализации шрифты уже скачаны в assets/fonts/ при инициализации проекта.
# Если нужно переустановить, просто удалите содержимое папки и запустите этот скрипт снова.

set -euo pipefail

FONT_DIR="$(dirname "$0")/assets/fonts"
mkdir -p "$FONT_DIR"

# Если шрифты уже есть — не качаем повторно
if [ -f "$FONT_DIR/Inter-Regular.ttf" ] && [ -f "$FONT_DIR/Inter-Bold.ttf" ] && [ -f "$FONT_DIR/Inter-ExtraBold.ttf" ] && [ -f "$FONT_DIR/Oswald-Regular.ttf" ] && [ -f "$FONT_DIR/Oswald-Bold.ttf" ]; then
  echo "✅ Шрифты уже установлены в $FONT_DIR"
  exit 0
fi

echo "🔄 Скачивание шрифтов Inter и Oswald..."

# Inter (Regular, Bold, ExtraBold)
for weight in Regular Bold ExtraBold; do
  curl -L -o "$FONT_DIR/Inter-${weight}.ttf" "https://github.com/googlefonts/Inter/raw/main/fonts/ttf/Inter-${weight}.ttf"
done

# Oswald (Regular, Bold)
for weight in Regular Bold; do
  curl -L -o "$FONT_DIR/Oswald-${weight}.ttf" "https://github.com/googlefonts/Oswald/raw/main/fonts/ttf/Oswald-${weight}.ttf"
done

echo "✅ Шрифты успешно скачаны в $FONT_DIR"