# Firestore-first setup for `coremedi-59bbc`

This repository now includes a conservative Firestore starter configuration. It is not deployed to your Firebase project by this commit; you must run the commands below from a trusted machine signed in to the correct Firebase account.

## Data layout

Use Firestore for patient and scan **metadata**, not binary `.glb` files:

```text
patients/{patientId}
  ownerUid: <Firebase Authentication UID>
  synthetic: true
  footScans/{scanId}
    laterality: "left" | "right"
    capturedAt: <timestamp or ISO-8601 string>
    fileFormat: "model/gltf-binary"
    storagePath: <optional future Storage object path>
    synthetic: true
```

For initial Firestore-only testing, omit `storagePath` and test metadata with synthetic values. The current static viewer does not read Firestore. Do not copy real patient information into sample records.

The included `firestore.rules` requires Firebase Authentication and allows a signed-in user to access only patient documents whose `ownerUid` matches their Firebase Auth UID. Scan metadata inherits access from its parent patient. This is a minimal single-owner prototype, not a complete clinic/team role model; do not broaden access rules to make a demo work.

## Setup and deploy rules

1. In Firebase Console, select project `coremedi-59bbc` and create/enable Cloud Firestore in the intended region. Choose the region carefully; it may be difficult to change later.
2. Enable a Firebase Authentication provider and create/sign in a test user. The Firestore `ownerUid` must be that user's Authentication UID.
3. From the repository root, install or use the Firebase CLI, sign in, and verify the selected project:

   ```bash
   npm install -g firebase-tools
   firebase login
   firebase use coremedi-59bbc
   firebase projects:list
   ```

4. Deploy only the Firestore security rules and index configuration:

   ```bash
   firebase deploy --only firestore:rules,firestore:indexes
   ```

5. In Firestore, create `patients/{synthetic-id}` with an `ownerUid` equal to your signed-in test user's UID and `synthetic: true`. Under it, create `footScans/{synthetic-scan-id}` with fields like `laterality: "right"`, `fileFormat: "model/gltf-binary"`, and `synthetic: true`. The current viewer remains local-only and will not fetch these records.

Do not use Firestore test mode or open rules. Verify that signed-out access and access by a different test account are denied before adding any sensitive data.

## Health-data warning

Do not put PHI, identifiable patient details, or real scans in this project until your organization has confirmed the required consent, access controls, retention, security configuration, and applicable contractual/compliance requirements for the specific Firebase services and region. A Firebase project ID alone does not establish that the project is approved for clinical data. This sample is not a clinical application or a validated data model.
