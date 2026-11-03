#!/usr/bin/env bash
# Master a rendered video for vertical social platforms.
#
#   pass 1  measure integrated loudness, true peak, loudness range (ffmpeg loudnorm, JSON)
#   pass 2  loudnorm with the measured values + a peak limiter on the audio; repeated with a raised aim
#           when limiting leaves it short; then H.264 High yuv420p tagged BT.709, AAC 48 kHz, faststart
#   check   measure the written file again (ebur128 with true peak) and fail when it misses the target
#
# One-pass loudnorm often stops short of the target when the input has hot peaks; the measured second
# pass and the limiter are what make the target reachable.
#
# Usage: master-social.sh INPUT OUTPUT [--lufs -14] [--tp -1.5] [--crf 16] [--in-matrix auto|bt601|bt709]
#   --in-matrix  colour matrix of INPUT. auto reads the tag; an untagged input is treated as BT.601
#                (ffmpeg's assumption) with a warning. The output is always converted to and tagged BT.709.
# Exit codes: 0 target met, 1 target missed, 2 usage or tool error.
set -euo pipefail

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 2; }
[ $# -ge 2 ] || usage
IN=$1; OUT=$2; shift 2
LUFS=-14; TP=-1.5; CRF=16; INM=auto
while [ $# -gt 0 ]; do
  case "$1" in
    --lufs) LUFS=$2; shift 2 ;;
    --tp) TP=$2; shift 2 ;;
    --crf) CRF=$2; shift 2 ;;
    --in-matrix) INM=$2; shift 2 ;;
    -h|--help) usage ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null || { echo "ffmpeg and ffprobe are required" >&2; exit 2; }
[ -f "$IN" ] || { echo "input not found: $IN" >&2; exit 2; }

if [ "$INM" = auto ]; then
  TAG=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_space -of csv=p=0 "$IN" | tr -d '[:space:]')
  case "$TAG" in
    bt709) INM=bt709 ;;
    smpte170m|bt470bg) INM=bt601 ;;
    *) INM=bt601; echo "warning: input has no colour matrix tag ('$TAG'); treating it as BT.601. Pass --in-matrix bt709 if it was rendered as BT.709." >&2 ;;
  esac
fi
VF="scale=in_color_matrix=$INM:out_color_matrix=bt709:in_range=tv:out_range=tv,format=yuv420p"

# Pass 1: measure. The JSON block is the last {...} in loudnorm's stderr output.
MEAS=$(ffmpeg -hide_banner -nostats -i "$IN" -vn -af "loudnorm=I=$LUFS:TP=$TP:LRA=11:print_format=json" -f null - 2>&1 |
  python3 -I -c 'import sys, json
t = sys.stdin.read()
d = json.loads(t[t.rindex("{"):t.rindex("}") + 1])
print(d["input_i"], d["input_tp"], d["input_lra"], d["input_thresh"], d["target_offset"])')
read -r MI MTP MLRA MTH OFF <<< "$MEAS"
echo "measured input: I=$MI LUFS, TP=$MTP dBTP, LRA=$MLRA LU"

# Limiter ceiling at the true-peak target (alimiter works on sample peaks; the check below measures true peak).
LIM=$(python3 -I -c "print(round(10 ** ($TP / 20), 4))")
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

measure() {  # integrated loudness and true peak of a file, as "I TP"
  ffmpeg -hide_banner -nostats -i "$1" -vn -af ebur128=peak=true:framelog=quiet -f null - 2>&1 |
    python3 -I -c 'import sys, re
t = sys.stdin.read()
s = t[t.rindex("Summary:"):]
i = re.search(r"I:[ ]+(-?[\d.]+) LUFS", s).group(1)
p = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", s).group(1)
print(i, p)'
}

# Pass 2 on the audio alone. When limiting eats loudness and the result falls short, the target is raised by
# the shortfall and pass 2 runs again (at most three attempts), so the video is encoded only once.
AIM=$LUFS
for attempt in 1 2 3; do
  ffmpeg -hide_banner -loglevel error -y -i "$IN" -vn \
    -af "loudnorm=I=$AIM:TP=$TP:LRA=11:measured_I=$MI:measured_TP=$MTP:measured_LRA=$MLRA:measured_thresh=$MTH:offset=$OFF:linear=false,alimiter=limit=$LIM:attack=1:release=50:level=disabled" \
    -ar 48000 -c:a pcm_f32le "$TMP/audio.wav"
  read -r AI ATP <<< "$(measure "$TMP/audio.wav")"
  SHORT=$(python3 -I -c "print(round($LUFS - $AI, 2))")
  echo "pass 2, attempt $attempt: aimed at $AIM, got I=$AI LUFS, true peak=$ATP dBFS"
  python3 -I -c "import sys; sys.exit(0 if abs($SHORT) <= 0.5 else 1)" && break
  AIM=$(python3 -I -c "print(round(min(-5.0, $AIM + $SHORT), 2))")
done

ffmpeg -hide_banner -loglevel error -y -i "$IN" -i "$TMP/audio.wav" -map 0:v:0 -map 1:a:0 -vf "$VF" \
  -c:v libx264 -preset slow -crf "$CRF" -profile:v high -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -movflags +faststart "$OUT"

# Check the written file, not the intent.
read -r OI OTP <<< "$(measure "$OUT")"
PIX=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt,color_space -of csv=p=0 "$OUT")
echo "output: I=$OI LUFS, true peak=$OTP dBFS, video=$PIX, file=$OUT"
python3 -I - "$OI" "$OTP" "$LUFS" "$TP" <<'PY'
import sys
oi, otp, target, tp = (float(v) if v != "-inf" else -99.0 for v in sys.argv[1:5])
problems = []
if abs(oi - target) > 1.0:
    problems.append(f"integrated loudness {oi} LUFS is more than 1 LU from {target}")
if otp > tp + 0.5:
    problems.append(f"true peak {otp} dBFS is above the {tp} dBTP ceiling")
if problems:
    print("FAIL: " + "; ".join(problems))
    sys.exit(1)
print("PASS: loudness and true peak within tolerance")
PY
