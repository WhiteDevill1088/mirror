# How to Use Morppy Mobile Mirror Suite

Morppy mirrors Android devices to a Windows PC and can receive AirPlay streams from Apple devices. This guide covers the packaged Windows application.

## Requirements

- 64-bit Windows 10 or Windows 11.
- For Android: a USB cable for USB mirroring, or a shared local network for wireless ADB.
- For AirPlay: the PC and Apple device on the same local network.
- The packaged `MorppyMirror.exe`. Python and separately installed ADB, scrcpy, QtScrcpy, or UxPlay are not needed when using a correctly built self-contained release.

The app does not require administrator privileges. Windows Firewall may ask whether to allow network access for wireless ADB or AirPlay. Allow access on **Private networks** only if you intend to use those features. Do not disable Windows security protections to launch an app.

## Start the application

1. Download `MorppyMirror.exe` from the official distributor.
2. Check that the file came from a trusted source and, if provided, compare its published hash. To inspect a signature, right-click the EXE, open **Properties > Digital Signatures**, select the signer, and check the signature details.
3. Double-click the EXE. On first run it extracts bundled runtime files into a temporary directory, so startup may take a little longer.
4. If Windows reports an unknown publisher or blocks the file, do not bypass the warning. Confirm the publisher and file with the distributor or request a properly signed release.

## Connect an Android phone or tablet

### USB connection

1. On the Android device, open **Settings > About phone** and tap **Build number** several times until Developer options are enabled. Menu wording differs by manufacturer.
2. In **Developer options**, enable **USB debugging**.
3. Connect the device to the PC with a data-capable USB cable and accept the device's USB debugging authorization prompt.
4. In Morppy, open **Devices**. Devices are scanned automatically; select **Refresh Devices** to scan immediately.
5. On the device card, select **Launch Mirror**. Choose the display options and select **Start Mirroring**.

If Android does not show the authorization prompt, unlock the phone, reconnect the cable, check the USB mode, and confirm USB debugging is enabled.

### Wireless ADB

1. Connect the phone and PC to the same trusted local network.
2. Enable **Developer options > Wireless debugging** on Android and complete Android's pairing/authorization step if it requests one.
3. Enter the device's current IP address and ADB connection port in the **Devices** page, for example `192.168.1.35:5555`, then select **Connect Wireless**.
4. Refresh the device list if the device does not appear.

The port and pairing process vary by Android version. Morppy connects to an `IP:port`; it does not provide Android's pairing-code workflow. Do not expose ADB to public or untrusted networks.

## Launch and control a mirror

On a connected device card:

- **Launch Mirror** opens session-specific engine, resolution, window size, renderer, and advanced display options.
- Choose **scrcpy 4.0 (Default)** for the standard mirror, or **QtScrcpy (Gaming Engine)** when you need its gaming/keymapping workflow.
- Leave resolution and renderer on their defaults unless you need to reduce bandwidth or troubleshoot rendering.
- **Reset Screen** returns changed Android display size/density to native defaults.
- **Screen Off** turns off the phone's physical display while the PC mirror remains active.
- **Lock** locks the device; **Reboot** asks for confirmation before rebooting it.
- The toolbar provides Power, volume, Back, Home, Recents, text/clipboard injection, and Screenshot actions.

Use the **Global Settings** page for default engine, bitrate, codec, audio forwarding, and session behavior. The header's **Preset** selector quickly applies a preset. The **Presets & History** page lets you apply, save, import, and export presets and review recent sessions.

## Record a device

1. Select **Start Recording** on the connected device card.
2. Choose the recording engine, file format, codec, and PC save folder.
3. Select **Start Recording** in the dialog.
4. Select the recording control again to stop. The recording is saved to the chosen folder.

For broad playback compatibility, use MP4 with H.264. H.265/HEVC can reduce file size but requires a compatible player. Ensure the selected save drive has enough free space.

## Receive AirPlay

1. Connect the iPhone, iPad, or Mac and the Windows PC to the same local network.
2. Open **iOS AirPlay** in Morppy and select **Launch AirPlay Mirror Receiver**.
3. On the Apple device, open Screen Mirroring/AirPlay and select **Morppy AirPlay Receiver**.
4. Use **Bring AirPlay to Front** if the stream window is behind another window. Select **Stop AirPlay Receiver** when finished.

Network isolation, guest Wi-Fi, VPNs, or firewall policy can prevent AirPlay device discovery. Keep the receiver on a trusted network.

## Choose an app theme

1. Open **Theme Studio**.
2. Preview **Cupertino Light**, **Hybrid Studio**, or **Midnight Glass**.
3. Choose **Light**, **Dark**, or **System** polarity.
4. Select **Apply theme** to apply and save the choice. **Restore defaults** selects Hybrid Studio with System appearance; apply it to commit the reset.

## Presets, history, and logs

- **Presets & History**: select **Apply** to use a preset, **Save Current** to create one, or **Import/Export** to move preset JSON files.
- **Recent Session History** lists recent mirror sessions and can be filtered with its search field.
- **Logs** shows app activity and provides **Clear Console Logs**.
- The app stores preferences and session data under `%LOCALAPPDATA%\MorppyMirror`.

## Troubleshooting

### No Android devices appear

- Unlock the device and accept its USB debugging prompt.
- Try a different USB cable or USB port; some cables are charge-only.
- Confirm USB debugging is enabled, then select **Refresh Devices**.
- For wireless connections, check that the IP address and port are current and that the PC and phone can communicate on the same network.
- Use **Reset ADB** only if the Android connection service appears stuck; it restarts the ADB server and may briefly disconnect devices.

### Mirror fails to start or looks incorrect

- Reconnect and authorize the device, then refresh the device list.
- Try the default scrcpy engine and native resolution first.
- If the GPU renderer fails, try another renderer in the session settings.
- Check **Logs** for app activity and consult the release distributor if the error persists.

### Windows blocks or warns about the EXE

An unsigned or newly signed application can trigger SmartScreen or unknown-publisher warnings. A trusted signature identifies the publisher but does not guarantee that all reputation-based prompts disappear. Verify the download with the distributor; do not turn off SmartScreen, Defender, or other security controls.

### Theme or preset preferences do not persist

Confirm that the current Windows user can write to `%LOCALAPPDATA%\MorppyMirror`. Theme preferences and presets are stored locally for that user.
