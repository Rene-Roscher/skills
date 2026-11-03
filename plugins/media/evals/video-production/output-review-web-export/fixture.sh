#!/usr/bin/env bash
set -euo pipefail
mkdir -p scripts
cat > remotion.config.ts <<'TS'
import {Config} from '@remotion/cli/config';
Config.setVideoImageFormat('png');
TS
cat > scripts/export-hero.sh <<'SH'
#!/usr/bin/env bash
# Hero video for the landing page. AV1 only, 10-bit for smoother gradients.
set -euo pipefail
ffmpeg -y -i out/hero-master.mov -c:v libsvtav1 -crf 30 -pix_fmt yuv420p10le -c:a libopus out/hero.webm
SH
