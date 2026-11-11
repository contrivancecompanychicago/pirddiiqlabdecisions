# Firebase-hosted 3D foot scan viewer

A small static viewer for binary glTF (`.glb`) foot scans. It is configured for Firebase project `coremedi-59bbc` and can be deployed with Firebase Hosting. It does not use Firestore or Cloud Storage: a selected scan is opened locally in the browser and is not uploaded or saved by this page.

## Deploy to Firebase Hosting

1. Install Node.js and the Firebase CLI: `npm install -g firebase-tools`.
2. From the repository root, sign in with an account that has access to `coremedi-59bbc`: `firebase login`.
3. Deploy the static site: `firebase deploy --only hosting`.

The included `.firebaserc` selects `coremedi-59bbc`, and `firebase.json` publishes only the `public/` directory. If this repository is already configured for Firebase Hosting, review the existing hosting setup before deploying so you do not overwrite another site's hosting configuration.

## Use

Open the deployed site, choose a `.glb` file (or drop one on the viewer), then drag to rotate and use scroll/pinch to zoom. The viewer requires an internet connection to load the model-viewer library from unpkg. Keep scans de-identified unless your organization's approved security and privacy controls permit otherwise.

This is a visualization-only prototype. It does not identify patients, persist scans, connect to the diabetes risk model, or provide a diagnosis. Risk-model integration and authenticated patient-data storage should be designed and clinically validated separately.
