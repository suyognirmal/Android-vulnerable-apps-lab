# Android Vulnerable Apps Lab

A curated collection of **legal, intentionally vulnerable** Android APKs for mobile application security training — static analysis, dynamic testing, and framework-specific reverse engineering. Use only on isolated emulators or lab devices. APK binaries are **not** committed to this repository; run the included scripts to download and build them locally.

### Why use this repo?

- **Verified download URLs** — `download_urls.json` lists direct links to 19 prebuilt APKs; run `python3 download_apps.py` to fetch them all
- **Easy automated builds** — `build_config.json` defines recipes for 5 apps without public releases; run `python3 build_apps.py` to clone, build, and place artifacts in the correct folders
- **Organized by framework** — consistent layout: `native-java/`, `native-kotlin/`, `jetpack-compose/`, `flutter/`, `react-native/`
- **Lightweight clone** — no large APK files in git; populate artifacts on demand
- **Upstream sources linked** — every app credits and links to its original open-source project
- **Broad stack coverage** — classic Java/Kotlin labs, Jetpack Compose, Flutter (AOT/`libapp.so`), React Native (plain bundle, Hermes, Expo) in one corpus

## Quick start

```bash
git clone https://github.com/suyognirmal/Android-vulnerable-apps-lab.git
cd android-vulnerable-apps-lab
python3 download_apps.py
python3 build_apps.py
```

Fetch a subset of apps:

```bash
python3 download_apps.py --only DIVA,VulnerableRN
python3 build_apps.py --only vulnapp
```

## Prerequisites

| Variable | Required for |
|----------|--------------|
| `ANDROID_SDK_ROOT` (or `ANDROID_HOME`) | Gradle builds (`VulnLab`, `VulnBankLab`) |
| `FLUTTER` or `flutter` on `PATH` | Flutter builds (`VulnApp`, `SecureBank-Starter`) |
| `JAVA_HOME` or `javac` on `PATH` | Gradle builds (auto-downloads Temurin 21 if missing) |
| `BUILD_TMP` | Optional scratch dir for git clones (defaults to system temp) |

```bash
export ANDROID_SDK_ROOT=/path/to/android/sdk
export FLUTTER=/path/to/flutter/bin/flutter
```

## Repository layout

```text
.
├── README.md
├── .gitignore
├── download_urls.json      # direct download URLs (19 apps)
├── build_config.json       # build recipes (5 apps)
├── download_apps.py
├── build_apps.py
├── native-java/
│   ├── DIVA/
│   ├── Sieve/
│   └── ...
├── native-kotlin/
│   ├── MSTG-Kotlin/
│   └── ...
├── jetpack-compose/
│   ├── HackDoor/
│   └── ...
├── flutter/
│   ├── DVFA/
│   └── ...
└── react-native/
    ├── VulnBank-RN/
    └── ...
```

Each app folder receives one APK after running the scripts: `{framework}/{AppName}/{artifact.apk}`.

## Native Java

| App | Description | Upstream |
|-----|-------------|----------|
| DIVA | Classic 13-challenge insecure app covering storage, IPC, and native code. | [payatu/diva-android](https://github.com/payatu/diva-android) |
| Sieve | Password manager lab app bundled with Drozer for IPC and content-provider testing. | [WithSecureLabs/drozer](https://github.com/WithSecureLabs/drozer) |
| InsecureBankv2 | Vulnerable banking app with weak crypto, exported components, and API flaws. | [dineshshetty/Android-InsecureBankv2](https://github.com/dineshshetty/Android-InsecureBankv2) |
| MSTG-Java | OWASP MASTG hacking playground — Java edition mapped to official test cases. | [OWASP/MASTG-Hacking-Playground](https://github.com/OWASP/MASTG-Hacking-Playground) |
| Damn-Vulnerable-Bank | Modern vulnerable banking app with root detection, pinning, and API abuse scenarios. | [rewanthtammana/Damn-Vulnerable-Bank](https://github.com/rewanthtammana/Damn-Vulnerable-Bank) |
| Vuldroid | Modular vulnerable app with WebView file theft and component exposure challenges. | [jaiswalakshansh/Vuldroid](https://github.com/jaiswalakshansh/Vuldroid) |
| UnCrackable-L1 | OWASP MASTG crackme L1 — root detection bypass and native string extraction. | [OWASP/mastg](https://github.com/OWASP/mastg) |
| UnCrackable-L2 | OWASP MASTG crackme L2 — tamper detection and runtime decryption. | [OWASP/mastg](https://github.com/OWASP/mastg) |
| UnCrackable-L3 | OWASP MASTG crackme L3 — white-box crypto and obfuscated native code. | [OWASP/mastg](https://github.com/OWASP/mastg) |
| UnCrackable-L4 | OWASP MASTG crackme L4 (r2Pay) — multi-layer native protection and white-box AES. | [OWASP/mastg](https://github.com/OWASP/mastg) |
| VulnLab | Comprehensive OWASP Mobile Top 10 lab covering IPC, WebView RCE, and dynamic code loading. | [anpa1200/Vulnerable-APK](https://github.com/anpa1200/Vulnerable-APK) |

## Native Kotlin

| App | Description | Upstream |
|-----|-------------|----------|
| MSTG-Kotlin | OWASP MASTG hacking playground — Kotlin edition with optional Rails backend. | [OWASP/MASTG-Hacking-Playground](https://github.com/OWASP/MASTG-Hacking-Playground) |
| InsecureShop | Kotlin e-commerce lab with deep links, WebView SSL issues, and intent redirection. | [optiv/InsecureShop](https://github.com/optiv/InsecureShop) |
| AndroGoat | OWASP-aligned Kotlin app with 25 vulnerability modules across storage and WebView. | [satishpatnayak/AndroGoat](https://github.com/satishpatnayak/AndroGoat) |

## Jetpack Compose

| App | Description | Upstream |
|-----|-------------|----------|
| HackDoor | Jetpack Compose forum app with OWASP Mobile Top 10 modules and optional Flask backend. | [macik09/Vulnforum](https://github.com/macik09/Vulnforum) |
| VulnBankLab | Compose banking demo with exported activities, deep-link auth bypass, and hardcoded credentials. | [deemoun/Vulnerable-Bank-App-Demo](https://github.com/deemoun/Vulnerable-Bank-App-Demo) |

## Flutter

| App | Description | Upstream |
|-----|-------------|----------|
| DVFA | OWASP FinTech Flutter lab with ten client-side challenges and optional mock backend. | [Schmiemandev/dvfa](https://github.com/Schmiemandev/dvfa) |
| Ostorlab-Insecure | Hybrid Java + Flutter scanner benchmark with 19+ vulnerability classes. | [Ostorlab/ostorlab_insecure_android_app](https://github.com/Ostorlab/ostorlab_insecure_android_app) |
| VulnApp | Beginner Flutter lab with hardcoded credentials, plain HTTP, and SharedPreferences tokens. | [chaseman447/VulnApp](https://github.com/chaseman447/VulnApp) |
| SecureBank-Starter | FortKnox vulnerable banking starter — drift/SQLite, deep links, and intentional OWASP flaws. | [team360r/SecureBank](https://github.com/team360r/SecureBank) |

## React Native

| App | Description | Upstream |
|-----|-------------|----------|
| VulnBank-RN | React Native banking app with hardcoded JWT and API keys in the JS bundle. | [Commando-X/vuln-bank-mobile](https://github.com/Commando-X/vuln-bank-mobile) |
| VulnerableRN | Payatu CTF app with a plain Metro JS bundle (no Hermes) for bundle RE practice. | [banditVedant/React-Native-CTF](https://github.com/banditVedant/React-Native-CTF) |
| RNHermes-CTF | Payatu CTF sibling app compiled with Hermes bytecode for RN Hermes analysis. | [banditVedant/React-Native-CTF](https://github.com/banditVedant/React-Native-CTF) |
| DemoSecret | Modern Expo + Hermes app with hardcoded demo secrets in the bundle. | [Incognito-Lab/DemoSecret-Mobile-App](https://github.com/Incognito-Lab/DemoSecret-Mobile-App) |

## Legal and attribution

All apps listed here are **intentionally vulnerable** and intended for **educational security research** on systems you own or are authorized to test. Do not use them against production systems or real user data.

APK binaries are fetched from upstream authors at clone/setup time and are **not** redistributed inside this git repository. Each app remains the property of its respective author; see the upstream links above for licenses and terms.

## Contributing

Pull requests welcome for broken download URLs, updated build recipes, and additional **legal** open-source vulnerable apps. Please do not submit commercial game APKs or copyrighted content.
