"""Tools for importing and exporting Onshape elements."""

import os
import tempfile

import httpx

from onshape_mcp.client import (
    BASE_URL,
    _make_headers,
    download_external_data,
    get,
    poll_translation,
    post,
)
from onshape_mcp.mcp_instance import mcp

# ── Async export helpers ───────────────────────────────────────────────────────


def _async_export(
    did: str,
    translation_url: str,
    payload: dict,
    file_suffix: str,
    timeout: int = 120,
) -> str:
    """Start an async translation, poll until complete, download result. Returns local file path."""
    result = post(translation_url, payload)
    translation_id = result.get("id", "")
    if not translation_id:
        raise RuntimeError(f"No translation ID returned: {result}")

    done = poll_translation(translation_id, timeout=timeout)
    external_ids = done.get("resultExternalDataIds", [])
    if not external_ids:
        raise RuntimeError("Translation completed but no result data IDs returned")

    return download_external_data(did, external_ids[0], suffix=file_suffix)


# ── Part Studio exports ────────────────────────────────────────────────────────


@mcp.tool()
def export_part_studio_step(
    did: str,
    wid: str,
    eid: str,
    part_ids: list[str] | None = None,
    configuration: str = "default",
    timeout: int = 120,
) -> str:
    """
    Export a Part Studio to STEP format. Returns the path of the downloaded file.

    part_ids: optional list of specific part IDs to export; exports all parts if omitted.
    configuration: encoded configuration string (use encode_configuration to generate).
    timeout: max seconds to wait for translation to complete.
    """
    payload: dict = {
        "formatName": "STEP",
        "documentId": did,
        "workspaceId": wid,
        "elementId": eid,
        "configuration": configuration,
        "storeInDocument": False,
    }
    if part_ids:
        payload["partIds"] = ",".join(part_ids)
    return _async_export(did, f"/api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/translations", payload, ".step", timeout)


@mcp.tool()
def export_part_studio_stl(
    did: str,
    wid: str,
    eid: str,
    part_id: str = "",
    units: str = "millimeter",
    angular_tolerance: float = 0.1,
    chord_tolerance: float = 0.1,
) -> str:
    """
    Synchronously export a Part Studio (or a single part) to STL format.
    Returns the path of the downloaded file.

    units: millimeter, centimeter, meter, inch, foot, yard
    """
    params: dict = {
        "units": units,
        "angularTolerance": angular_tolerance,
        "chordTolerance": chord_tolerance,
    }
    if part_id:
        params["partId"] = part_id

    from onshape_mcp.client import get_binary
    data = get_binary(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/stl", **params)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as f:
        f.write(data)
        return f.name


@mcp.tool()
def export_part_studio_gltf(
    did: str,
    wid: str,
    eid: str,
    configuration: str = "default",
    timeout: int = 120,
) -> str:
    """
    Export a Part Studio to glTF format. Returns the path of the downloaded file.
    """
    payload = {
        "formatName": "GLTF",
        "documentId": did,
        "workspaceId": wid,
        "elementId": eid,
        "configuration": configuration,
        "storeInDocument": False,
    }
    return _async_export(did, f"/api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/translations", payload, ".gltf", timeout)


@mcp.tool()
def export_part_studio_parasolid(
    did: str,
    wid: str,
    eid: str,
    configuration: str = "default",
) -> str:
    """
    Synchronously export a Part Studio to Parasolid format.
    Returns the path of the downloaded file.
    """
    from onshape_mcp.client import get_binary
    params: dict = {}
    if configuration and configuration != "default":
        params["configuration"] = configuration
    data = get_binary(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/parasolid", **params)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".x_t") as f:
        f.write(data)
        return f.name


# ── Assembly exports ───────────────────────────────────────────────────────────


@mcp.tool()
def export_assembly_step(
    did: str,
    wid: str,
    eid: str,
    configuration: str = "default",
    timeout: int = 120,
) -> str:
    """
    Export an Assembly to STEP format. Returns the path of the downloaded file.
    """
    payload = {
        "formatName": "STEP",
        "documentId": did,
        "workspaceId": wid,
        "elementId": eid,
        "configuration": configuration,
        "storeInDocument": False,
    }
    return _async_export(did, f"/api/v10/assemblies/d/{did}/w/{wid}/e/{eid}/translations", payload, ".step", timeout)


@mcp.tool()
def export_assembly_gltf(
    did: str,
    wid: str,
    eid: str,
    configuration: str = "default",
    timeout: int = 120,
) -> str:
    """
    Export an Assembly to glTF format. Returns the path of the downloaded file.
    """
    payload = {
        "formatName": "GLTF",
        "documentId": did,
        "workspaceId": wid,
        "elementId": eid,
        "configuration": configuration,
        "storeInDocument": False,
    }
    return _async_export(did, f"/api/v10/assemblies/d/{did}/w/{wid}/e/{eid}/translations", payload, ".gltf", timeout)


@mcp.tool()
def export_assembly_obj(
    did: str,
    wid: str,
    eid: str,
    configuration: str = "default",
    timeout: int = 120,
) -> str:
    """
    Export an Assembly to OBJ format. Returns the path of the downloaded file.
    """
    payload = {
        "formatName": "OBJ",
        "documentId": did,
        "workspaceId": wid,
        "elementId": eid,
        "configuration": configuration,
        "storeInDocument": False,
    }
    return _async_export(did, f"/api/v10/assemblies/d/{did}/w/{wid}/e/{eid}/translations", payload, ".obj", timeout)


# ── Translation status ─────────────────────────────────────────────────────────


@mcp.tool()
def get_translation_status(translation_id: str) -> dict:
    """
    Get the status of a translation (export) job.

    requestState will be one of: ACTIVE, DONE, FAILED.
    When DONE, resultExternalDataIds contains the blob IDs to download.
    """
    return get(f"/api/v10/translations/{translation_id}")


# ── Import ─────────────────────────────────────────────────────────────────────


@mcp.tool()
def import_file(
    did: str,
    wid: str,
    file_path: str,
    allow_faulty_parts: bool = False,
    import_in_background: bool = False,
) -> dict:
    """
    Import a CAD file into an Onshape document as a new element.

    file_path: absolute path to the local file to upload.
    Supported formats include STEP, IGES, STL, OBJ, DXF, DWG, Parasolid, ACIS, and others.
    Returns translation job info including the translation ID for status polling.
    """
    from urllib.parse import urlencode

    filename = os.path.basename(file_path)
    params_dict = {
        "storeInDocument": "true",
        "allowFaultyParts": str(allow_faulty_parts).lower(),
        "importInBackground": str(import_in_background).lower(),
    }
    query = urlencode(params_dict)
    path = f"/api/v10/documents/d/{did}/w/{wid}/blobs/translationFormats"
    headers = _make_headers("POST", path, query, "")
    # Remove Content-Type — let httpx set it for multipart
    headers.pop("Content-Type", None)
    headers["Accept"] = "application/json;charset=UTF-8; qs=0.09"

    url = f"{BASE_URL}{path}"
    with open(file_path, "rb") as f:
        file_data = f.read()

    with httpx.Client(timeout=60) as client:
        resp = client.post(
            url,
            headers=headers,
            params=params_dict,
            files={"file": (filename, file_data)},
        )
        resp.raise_for_status()
        return resp.json()
