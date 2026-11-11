"""Generate a clearly synthetic, stylized left-foot demo model as a GLB.

This is a simple 3D illustration for testing the viewer, not a patient scan,
anatomical reference, or clinical measurement.

Usage:
    python -m pip install trimesh
    python firebase/examples/generate_demo_left_foot.py

Writes demo-patient-001-left-foot.glb in the current directory.
"""

from pathlib import Path

import trimesh


def ellipsoid(name: str, center: tuple[float, float, float],
              radii: tuple[float, float, float], color: tuple[int, int, int, int]) -> trimesh.Trimesh:
    """Return a smooth colored ellipsoid component for the demo model."""
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    mesh.apply_scale(radii)
    mesh.apply_translation(center)
    mesh.visual.face_colors = color
    mesh.metadata["name"] = name
    return mesh


def main() -> None:
    # Coordinate convention: toes point toward +Y; the big toe sits on the
    # medial (+X) side. Dimensions are illustrative and are not measurements.
    skin = (206, 154, 126, 255)
    sole = (116, 77, 66, 255)
    meshes = [
        ellipsoid("sole-and-midfoot", (0.0, 0.015, 0.055), (0.060, 0.158, 0.043), sole),
        ellipsoid("heel", (0.0, -0.105, 0.074), (0.067, 0.070, 0.054), skin),
        ellipsoid("arch-and-instep", (0.0, -0.015, 0.100), (0.050, 0.112, 0.047), skin),
        ellipsoid("forefoot", (0.0, 0.105, 0.080), (0.086, 0.070, 0.045), skin),
        # Big toe is on the medial side; the smaller toes fan outward.
        ellipsoid("toe-1-medial", (0.049, 0.184, 0.071), (0.026, 0.055, 0.031), skin),
        ellipsoid("toe-2", (0.014, 0.193, 0.069), (0.021, 0.050, 0.027), skin),
        ellipsoid("toe-3", (-0.018, 0.188, 0.067), (0.019, 0.044, 0.024), skin),
        ellipsoid("toe-4", (-0.046, 0.175, 0.065), (0.017, 0.037, 0.022), skin),
        ellipsoid("toe-5-lateral", (-0.068, 0.157, 0.063), (0.016, 0.031, 0.020), skin),
    ]

    scene = trimesh.Scene()
    for mesh in meshes:
        name = str(mesh.metadata["name"])
        scene.add_geometry(mesh, node_name=name, geom_name=name)

    scene.metadata.update({
        "title": "Synthetic stylized left foot demo",
        "description": (
            "Procedurally generated illustrative model for testing a 3D viewer. "
            "Not a real scan, clinical anatomy, or a diagnostic/measurement model."
        ),
        "laterality": "left",
        "synthetic": True,
    })
    output = Path("demo-patient-001-left-foot.glb")
    output.write_bytes(scene.export(file_type="glb"))
    print(f"Created {output.resolve()} ({output.stat().st_size:,} bytes)")
    print("Synthetic illustration only — not a patient scan or clinical model.")


if __name__ == "__main__":
    main()
