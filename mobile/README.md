# ASTRA-MED Mobile (Expo)

Expo / React Native starter client. It provides an initial mobile shell and backend connectivity check. It is not yet the completed offline-capable clinical app.

## Setup
Requires Node.js LTS and Expo-compatible tooling.

```bash
cd mobile
npm install
```

Set the backend URL before starting. For a physical phone, use your computer's LAN IPv4 address, not `localhost`:

Windows CMD:
```cmd
set EXPO_PUBLIC_API_URL=http://192.168.1.10:8000
npx expo start
```

Replace `192.168.1.10` with the development computer's LAN address. Keep the phone and computer on the same trusted network. Do not expose the development API to the public internet.

Next mobile implementation: secure sign-in with `expo-secure-store`, encrypted offline queue, idempotent sync, notification permissions and API-backed profile/telemetry screens.
