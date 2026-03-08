import os
from tutor import hooks

HERE = os.path.dirname(__file__)

# ------------------------------------------------------------------
# 1) Make Tutor aware of our templates directory
# ------------------------------------------------------------------
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(os.path.join(HERE, "templates"))

# Map templates/custom_i18n/* into the MFE build context:
#   env/plugins/mfe/build/mfe/custom_i18n/*
hooks.Filters.ENV_TEMPLATE_TARGETS.add_item(
    (
        "custom_i18n",
        "plugins/mfe/build/mfe/custom_i18n",
    )
)

# ------------------------------------------------------------------
# 2) Copy shim into image during MFE build
# ------------------------------------------------------------------
hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-dockerfile-post-npm-install",
        r"""
# Inject Georgian ISO language shim
COPY custom_i18n/ /openedx/custom_i18n/
""",
    )
)

# ------------------------------------------------------------------
# 3) Webpack alias (DEV) - guarded
# ------------------------------------------------------------------
hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-webpack-dev-config",
        r"""
if (config && config.resolve) {
  config.resolve.alias = {
    ...(config.resolve.alias || {}),
    "i18n-iso-languages": "/openedx/custom_i18n/i18n-shim.js",
  };
}
""",
    )
)

# ------------------------------------------------------------------
# 4) Webpack alias (PROD) - best-effort for both @edx and @openedx frontend-build
# ------------------------------------------------------------------
# ------------------------------------------------------------------
# 4) Webpack alias (PROD) - Use heredoc to avoid line-break errors
# ------------------------------------------------------------------
hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-dockerfile-pre-npm-build",
        r"""
# Use a heredoc to prevent Docker parsing errors with 'fi' and 'done'
RUN <<'EOF'
set -eu
for f in \
  node_modules/@openedx/frontend-build/config/webpack.prod.config.js \
  node_modules/@edx/frontend-build/config/webpack.prod.config.js
do
  if [ -f "$f" ]; then
    echo "Patching alias in $f"
    node - "$f" <<'NODE' || true
const fs = require("fs");
const path = process.argv[1];
let s = fs.readFileSync(path, "utf8");
if (s.includes("i18n-iso-languages")) process.exit(0);

const aliasObj = /alias\s*:\s*\{([\s\S]*?)\}/m;
if (aliasObj.test(s)) {
  s = s.replace(aliasObj, (m, inner) => {
    const t = inner.trim();
    const sep = t.endsWith(",") || t.length === 0 ? "" : ",";
    return `alias: {${inner}${sep} "i18n-iso-languages": "/openedx/custom_i18n/i18n-shim.js" }`;
  });
  fs.writeFileSync(path, s, "utf8");
  process.exit(0);
}

const resolveBlock = /resolve\s*:\s*\{/m;
if (resolveBlock.test(s)) {
  s = s.replace(resolveBlock, (m) =>
    `${m}\n    alias: { "i18n-iso-languages": "/openedx/custom_i18n/i18n-shim.js" },`
  );
  fs.writeFileSync(path, s, "utf8");
}
process.exit(0);
NODE
  fi
done
EOF
""",
    )
)

# ------------------------------------------------------------------
# 5) Account MFE picker patch (robust) - js/ts/tsx + glob search
# ------------------------------------------------------------------
hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-dockerfile-pre-npm-build-account",
        r"""
RUN python3 - <<'PY'
from pathlib import Path
import re
import sys

# Look for constants.js/ts/tsx under any site-language folder
candidates = []
for ext in ("js", "ts", "tsx"):
    candidates.extend(Path("src").glob(f"**/site-language/**/constants.{ext}"))
    candidates.extend(Path("src").glob(f"**/site-language/constants.{ext}"))

if not candidates:
    print("Account picker patch: no constants.(js|ts|tsx) under src/**/site-language/**; skipping")
    sys.exit(0)

# Choose the most likely canonical path first
candidates = sorted(candidates, key=lambda p: (len(str(p)), str(p)))
p = candidates[0]
print(f"Account picker patch: patching {p}")

s = p.read_text(encoding="utf-8")

# Replace siteLanguageList (matches your earlier working pattern)
new_list = (
    "const siteLanguageList = ["
    "{ code: 'en', name: 'English', released: true },"
    "{ code: 'de', name: 'Deutsch', released: true },"
    "{ code: 'fr', name: 'Français', released: true },"
    "{ code: 'es', name: 'Español', released: true },"
    "{ code: 'ru', name: 'Русский', released: true },"
    "{ code: 'ka', name: 'ქართული', released: true }"
    "];"
)

pattern = r"const\s+siteLanguageList\s*=\s*\[[\s\S]*?\];"
s2, n = re.subn(pattern, new_list, s, count=1)

if n != 1:
    raise SystemExit(f"Account picker patch: failed to replace siteLanguageList in {p}")

p.write_text(s2, encoding="utf-8")
print("Account picker patch: OK")
PY
""",
    )
)
