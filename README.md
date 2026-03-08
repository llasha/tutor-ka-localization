# tutor-ka-localization

This is a v1 plugin for **Tutor v21** that enables adding a new (previously unsupported) language locale (e.g., Georgian `ka`) to the **MFE side** of Open edX.

This plugin affects only the MFE translation layer.  
As for LMS/CMS Django translations, they must be handled separately (see the companion plugin:  
https://github.com/llasha/tutor-ka-locale).

---

## Purpose

Open edX pulls official translations from Transifex via Atlas.  
If a locale does not yet exist upstream, this plugin allows you to:

- Register a new MFE locale
- Inject compiled translation files
- - Rebuild the Open edX MFE image with frontend language support

---

### 0. Prepare Your Fork (Required)

Fork this repository and update the source code to include your language locale (e.g., `ka`).  
Then clone **your fork** (not the upstream repository) in the next step.

tutor-ka-localization/
└── tutor_ka_localization/
    └── templates/
        └── custom_i18n/
            └── <your-locale>.json

This file should contain your compiled MFE translation catalog.
Without this file, the plugin will build successfully but no translations will be injected into the MFEs.

---

## Installation

### 1. Clone the Plugin

Change to the Tutor plugins directory (create it if necessary) and clone the repository:

```bash
mkdir -p "$(tutor plugins printroot)"
cd "$(tutor plugins printroot)"
git clone https://github.com/<your-user>/tutor-ka-localization
```

---

### 2. Install and Enable

```bash
cd "$(tutor plugins printroot)"
pip install -e tutor-ka-localization
tutor plugins enable ka_localization
tutor config save
```

---

## (Optional) Use a Custom `openedx-translations` Fork

Starting from Tutor v19, Open edX translations are managed by **Atlas**, which pulls translation files from the `openedx-translations` repository.

If you are using a fork of `openedx-translations`, set:

```bash
tutor config save \
  --set ATLAS_REPOSITORY="l1ph0x/openedx-translations" \
  --set ATLAS_REVISION="release/ulmo-ka.1"
```

Adjust the revision/tag as needed.

---

## 3. Rebuild Open edX MFE Image

Rebuild the Open edX MFE image to apply changes:

```bash
tutor images build mfe --no-cache
```

This may take about 40 minutes.

---

## Tag and Use the New Image

After the build completes:

```bash
docker tag overhangio/openedx-mfe:21.0.1 overhangio/openedx-mfe:21.0.1-ka-1
tutor config save --set MFE_DOCKER_IMAGE=overhangio/openedx-mfe:21.0.1-ka-1
```

(Optional) Verify:

```bash
tutor config printvalue MFE_DOCKER_IMAGE
```

---

## Restart Tutor

```bash
tutor local stop
tutor local start -d
```

---

## Compatibility: Tested & Works With

- Tutor v21

---


## License

Licensed under the Apache License, Version 2.0 (Apache-2.0).

See the LICENSE file for details.
