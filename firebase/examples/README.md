# Synthetic Firebase foot-scan examples

These examples demonstrate metadata for fictional patient `demo-patient-001`. They contain no real patient information and no scan files. Do not copy real patient information into this repository.

## Generate synthetic left/right foot GLBs

The generated files are stylized 3D illustrations for testing the viewer. They are not real scans, clinical anatomy, or diagnostic/measurement models.

From the repository root, run:

```bash
python -m pip install trimesh
python firebase/examples/generate_demo_left_foot.py
python firebase/examples/generate_demo_right_foot.py
```

This creates `demo-patient-001-left-foot.glb` and `demo-patient-001-right-foot.glb` in your current directory. Open the viewer and choose either file to test rotation and zoom. To upload a generated demo to Firebase Storage for a separate integration test, use Firebase Console and save it under a path such as `foot-scans/demo-patient-001/demo-patient-001-right-foot.glb`. The current viewer does not read Firebase Storage; the generated file is not automatically uploaded.

`demo-right-foot-scan.json` contains synthetic Firestore metadata for the right-foot example. Treat its `storagePath` as a sample path; the corresponding file must be uploaded separately if you want to test Storage.

## Firestore documents

Create a private Firestore collection at `patients`, then add a document with ID `demo-patient-001`. Under it, create a subcollection named `footScans` and add documents using synthetic IDs. The `foot-scan-records.json` file contains two sample left-foot records; `demo-right-foot-scan.json` contains a sample right-foot record.

Example document paths:

- `patients/demo-patient-001/footScans/scan-2026-01-15`
- `patients/demo-patient-001/footScans/scan-2026-04-15`
- `patients/demo-patient-001/footScans/demo-right-foot`

## Easiest safe first step

1. In Firebase Console, confirm project `coremedi-59bbc` is selected.
2. Enable Firestore Database and Cloud Storage only if your project does not already have them.
3. Keep test data synthetic. Generate the demo `.glb` files above and open them directly in the viewer; no Firebase upload is needed to test the viewer.
4. If you also want to test Storage, upload a generated synthetic `.glb` to a private Storage bucket. Do not include names, dates of birth, medical record numbers, or other direct identifiers in paths or document IDs.
5. Keep Storage and Firestore private. Require Firebase Authentication and enforce per-user access in security rules before using any real scans. Do not deploy permissive test-mode rules or put service-account credentials in frontend code or this repository.
6. For the simplest demo today, deploy the current Hosting viewer and choose the `.glb` file from your device. It stays in the browser; it is not saved to Firebase. Connecting the viewer to Firebase Storage requires a separate authenticated integration and security rules.

The examples are illustrative, not a clinical data schema or a clinical risk score. Follow your organization’s privacy, consent, retention, and security requirements before handling patient scans.
