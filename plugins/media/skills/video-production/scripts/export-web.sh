#!/usr/bin/env bash
# Export a finished master for a web page's own video player: an 8-bit AV1 file as the first source and an
# H.264 file as the fallback, both yuv420p, faststart, with the colour matrix tagged.
#
# Never 10-bit: a 10-bit AV1 file played with sound and a black picture in Chromium-based browsers with GPU
# decoding in one measured setup, while 8-bit AV1 and H.264 showed the picture. The script refuses to write
# anything but 8-bit 4:2:0.
#
# Usage: export-web.sh MASTER OUTDIR NAME [--matrix bt601|bt709] [--max-mib 24] [--av1-crf 32] [--gain-db 0]
#   --matrix   matrix to write and tag (default bt601, tagged smpte170m with BT.709 primaries and transfer).
#              The master is converted when its own tag differs; an untagged master is treated as BT.601.
#   --max-mib  size ceiling per file; the H.264 CRF is raised until the file fits, AV1 fails loudly.
#   --gain-db  optional level change before a -1.5 dBFS peak limiter (web players do not normalise loudness).
# Writes OUTDIR/NAME.av1.mp4 and OUTDIR/NAME.h264.mp4 and prints codec, pixel format, colour tags, size and
# loudness of each. Exit codes: 0 written and checked, 1 a check failed, 2 usage or tool error.
set -euo pipefail

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 2; }
[ $# -ge 3 ] || usage
M=$1; OUT=$2; N=$3; shift 3
MATRIX=bt601; MAXMIB=24; AV1CRF=32; GAIN=0
while [ $# -gt 0 ]; do
  case "$1" in
    --matrix) MATRIX=$2; shift 2 ;;
    --max-mib) MAXMIB=$2; shift 2 ;;
    --av1-crf) AV1CRF=$2; shift 2 ;;
    --gain-db) GAIN=$2; shift 2 ;;
    -h|--help) usage ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null || { echo "ffmpeg and ffprobe are required" >&2; exit 2; }
case "$(ffmpeg -hide_banner -encoders 2>/dev/null)" in *libsvtav1*) ;; *) echo "this ffmpeg has no libsvtav1 encoder" >&2; exit 2 ;; esac
[ -f "$M" ] || { echo "master not found: $M" >&2; exit 2; }
mkdir -p "$OUT"

case "$MATRIX" in
  bt601) TAGS=(-colorspace smpte170m -color_primaries bt709 -color_trc bt709 -color_range tv) ;;
  bt709) TAGS=(-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv) ;;
  *) echo "--matrix must be bt601 or bt709" >&2; exit 2 ;;
esac
SRC=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_space -of csv=p=0 "$M" | tr -d '[:space:]')
case "$SRC" in
  bt709) SRCM=bt709 ;;
  smpte170m|bt470bg) SRCM=bt601 ;;
  *) SRCM=bt601; echo "note: master has no matrix tag ('$SRC'); treated as BT.601" >&2 ;;
esac
if [ "$SRCM" = "$MATRIX" ]; then
  VF="format=yuv420p"
else
  VF="scale=in_color_matrix=$SRCM:out_color_matrix=$MATRIX:in_range=tv:out_range=tv,format=yuv420p"
  echo "converting matrix $SRCM -> $MATRIX"
fi
AF="volume=${GAIN}dB,alimiter=limit=0.84:attack=5:release=60:level=disabled"
LIMIT=$(python3 -I -c "print(int($MAXMIB * 1024 * 1024))")

ffmpeg -hide_banner -loglevel error -y -i "$M" -vf "$VF" -c:v libsvtav1 -preset 6 -crf "$AV1CRF" -g 240 \
  -pix_fmt yuv420p "${TAGS[@]}" -af "$AF" -c:a aac -b:a 192k -movflags +faststart "$OUT/$N.av1.mp4"
crf=20
while :; do
  ffmpeg -hide_banner -loglevel error -y -i "$M" -vf "$VF" -c:v libx264 -preset slow -crf $crf -profile:v high \
    -pix_fmt yuv420p "${TAGS[@]}" -af "$AF" -c:a aac -b:a 192k -movflags +faststart "$OUT/$N.h264.mp4"
  [ "$(stat -c %s "$OUT/$N.h264.mp4")" -le "$LIMIT" ] && break
  [ $crf -ge 35 ] && { echo "H.264 does not fit $MAXMIB MiB even at CRF 35" >&2; exit 1; }
  crf=$((crf + 1))
done

fail=0
for f in "$OUT/$N.av1.mp4" "$OUT/$N.h264.mp4"; do
  info=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,pix_fmt,color_space,color_primaries,color_transfer -of csv=p=0 "$f")
  size=$(stat -c %s "$f")
  loud=$(ffmpeg -hide_banner -nostats -i "$f" -vn -af ebur128=peak=true:framelog=quiet -f null - 2>&1 | grep -E '^\s+(I|Peak):' | tr -s ' ' | tr '\n' ' ')
  echo "$(basename "$f"): $info, $((size / 1024)) KiB, $loud"
  case "$info" in *yuv420p,*) ;; *) echo "FAIL: $(basename "$f") is not 8-bit yuv420p" >&2; fail=1 ;; esac
  [ "$size" -le "$LIMIT" ] || { echo "FAIL: $(basename "$f") is over $MAXMIB MiB" >&2; fail=1; }
done
echo "h264 crf $crf"
exit $fail
