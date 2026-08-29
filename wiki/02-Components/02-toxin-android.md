# Toxin — Android Prototype

> Phase 6 — Mobile spawn for Symbiote-OS

## Status: **Build Ready** ✅

### What Works
- ✅ Debug APK built (5.5 MB) at `app/build/outputs/apk/debug/app-debug.apk`
- ✅ Status dashboard with component tracking
- ✅ Adaptive launcher icon
- ✅ Themed UI (Material3 dark theme)
- ✅ Build.gradle configured with dependencies

### Setup Requirements
| Line | Path | Version |
|------|------|---------|
| **Android Studio** | `/opt/android-studio/` | AI-261.26222.65.2613.16025427 |
| **Android SDK** | `~/Android/Sdk/` | platform-tools 37.0.1, build-tools 34.0.0 |
| **AVD (microG)** | `~/.android/avd/Toxin-microG-API34.avd` | Android 14, x86_64, AOSP (clean, no Google stubs) |
| **AVD (Google APIs)** | `~/.android/avd/Toxin-Pixel4XL-API34.avd` | Android 14, x86_64, google_apis |
| **KVM accel** | `/dev/kvm` | ✅ Active on portable SSD host |
- ⏳ **Android device** (LineageOS + microG recommended)
- ⏳ **TWRP recovery** for ROM flashing (if needed)

## microG (Not GApps)

This project uses **microG** instead of full GApps for:
- ✅ Gmail, Maps, Drive, Contacts, YouTube
- ❌ Google Pay, YouTube Premium (hardware attestation required)

### Installation on Emulator (Development)

**microG is pre-installed on the Toxin-microG-API34 AVD:**
- ✅ microG GmsCore v0.3.15.250932 running (PID auto-launched)
- ✅ GsfProxy installed
- ✅ UnifiedNlp v1.6.8 installed
- ✅ Aurora Store v4.8.4 installed
- ✅ F-Droid installed
- ✅ x86_64 native libs with KVM acceleration

```bash
# Start the microG emulator
~/bin/toxin-emulator

# Or manually:
$ANDROID_HOME/emulator/emulator -avd "Toxin-microG-API34" -no-snapshot -accel on

# Verify microG is running
adb shell ps | grep microg
```

### Installation on Device

1. **Flash LineageOS** (with microG support)
   - Or install via F-Droid:
   - Add repo: `https://microg.github.io/fdroid.xml`
   - Install: `com.google.android.gms` (microg), `FakeStore`, `GsfProxy`, `GmsCore`

2. **Grant system permissions** (requires root/Magisk)
3. **Enable microG in Settings**

## Android Project Structure

```
toxin/
├── build.gradle                       # Project-level (completed)
├── settings.gradle                    # Module declaration
├── gradle.properties                  # Build properties
├── proguard-rules.pro                 # MicroG-compatible rules
├── scripts/
│   └── setup-toxin.sh                 # Setup automation script
├── README.md                          # This file
└── app/
    ├── build.gradle                   # App-level Gradle (completed)
    └── src/main/
        ├── java/com/example/toxin/
        │   └── MainActivity.kt        # Status dashboard
        ├── res/
        │   ├── layout/
        │   │   └── activity_main.xml  # Dashboard layout
        │   ├── values/
        │   │   ├── strings.xml        # App strings
        │   │   ├── colors.xml         # Threat model colors
        │   │   └── themes.xml         # Dark theme
        │   └── mipmap-anydpi-v26/
        │       └── ic_launcher.xml    # Adaptive launcher
        └── AndroidManifest.xml
```

## Quick Setup Commands

```bash
# Build APK
cd ~/projects/symbiote-os/toxin
export ANDROID_HOME=~/Android/Sdk
/opt/android-studio/bin/studio.sh  # Launch Android Studio

# Or headless Gradle build:
gradle assembleDebug

# Install on emulator
adb install app/build/outputs/apk/debug/app-debug.apk

# Install on connected device
~/Android/Sdk/platform-tools/adb install app/build/outputs/apk/debug/app-debug.apk

# Run setup script (device must be connected)
./scripts/setup-toxin.sh
```

### Running Toxin

```bash
# Launch Toxin on emulator
adb shell monkey -p com.example.toxin -c android.intent.category.LAUNCHER 1

# Or via Android Studio:
#   Run → app (on emulator Toxin-microG-API34)
```

## Component Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Build** | ✅ Ready | APK at `app/build/outputs/apk/debug/` |
| **microG (emulator)** | ✅ Running | Pre-installed on Toxin-microG-API34 AVD |
| **microG (device)** | ✅ Ready | Install on LineageOS device |
| **Syncthing** | ⏳ Pending | Hive sync |
| **Shelter** | ⏳ Pending | Work profile isolation |
| **Tor** | ⏳ Pending | Onion service bridge |

See also:
- `~/.symbiote-brain/` on Venom desktop for the shared vault
- `SYMBIOTE_TENDRIL_TOXIN_INTEGRATION.md` for Tor bridge setup