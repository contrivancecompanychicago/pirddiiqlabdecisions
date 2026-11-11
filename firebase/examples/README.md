# Synthetic Firebase foot-scan examples

These examples demonstrate metadata for two scans belonging to the same **fictional** patient. They contain no real patient information and no scan files. Do not copy real patient information into this repository.

## Generate a sample left-foot GLB

The generated file is a stylized, synthetic 3D illustration for testing the viewer. It is not a real scan, clinical anatomy, or a diagnostic/measurement model.

From the repository root, run:

```bash
python -m pip install trimesh
python firebase/examples/generate_demo_left_foot.py
```

This creates `demo-patient-001-left-foot.glb` in your current directory. Open the viewer and choose that file to test rotation and zoom. To upload it to Firebase Storage for a separate integration test, use Firebase Console and save it under a path such as `foot-scans/demo-patient-001/demo-patient-001-left-foot.glb`. The current viewer does not read Firebase Storage; the generated file is not automatically uploaded.

## Firestore documents

Create a private Firestore collection at `patients`, then add a document with ID `demo-patient-001`. Under it, create a subcollection named `footScans` and add these two documents using the IDs shown below. The JSON file `foot-scan-records.json` contains the fields and values for both records.

Example document paths:

- `patients/demo-patient-001/footScans/scan-2026-01-15`
- `patients/demo-patient-001/footScans/scan-2026-04-15`

The `storagePath` values are examples only. Upload an authorized `.glb` scan to the corresponding private Firebase Storage location before using a record in an app. This repository's current viewer opens a local file and does not read Firestore or Storage.

## Easiest safe first step

1. In Firebase Console, confirm project `coremedi-59bbc` is selected.
2. Enable Firestore Database and Cloud Storage only if your project does not already have them.
3. Keep test data synthetic. Generate the demo `.glb` above and open it directly in the viewer; no Firebase upload is needed to test the viewer.
4. If you also want to test Storage, upload this synthetic `.glb` to a private Storage bucket. Do not include names, dates of birth, medical record numbers, or other direct identifiers in paths or document IDs.
5. Keep Storage and Firestore private. Require Firebase Authentication and enforce per-user access in security rules before using any real scans. Do not deploy permissive test-mode rules or put service-account credentials in frontend code or this repository.
6. For the simplest demo today, deploy the current Hosting viewer and choose the `.glb` file from your device. It stays in the browser; it is not saved to Firebase. Connecting the viewer to Firebase Storage requires a separate authenticated integration and security rules.

The examples are illustrative, not a clinical data schema or a clinical risk score. Follow your organization’s privacy, consent, retention, and security requirements before handling patient scans.
