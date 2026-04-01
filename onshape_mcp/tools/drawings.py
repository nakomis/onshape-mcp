"""Tools for Onshape Drawing operations."""

from onshape_mcp.client import get, post
from onshape_mcp.mcp_instance import mcp


@mcp.tool()
def create_drawing(
    did: str,
    wid: str,
    name: str,
    part_studio_eid: str = "",
    assembly_eid: str = "",
    drawing_params: dict | None = None,
) -> dict:
    """
    Create a new Drawing tab in a document workspace.

    Optionally link it to a Part Studio or Assembly element for automatic view generation.
    drawing_params: additional BTModelElementParams fields (e.g. templateDocumentId, size, units).
    """
    payload: dict = {"name": name}
    if drawing_params:
        payload.update(drawing_params)
    if part_studio_eid:
        payload["elementId"] = part_studio_eid
    elif assembly_eid:
        payload["elementId"] = assembly_eid

    result = post(f"/api/v10/drawings/d/{did}/w/{wid}", payload)
    return {"id": result.get("id", ""), "name": result.get("name", name)}


@mcp.tool()
def modify_drawing(did: str, wid: str, eid: str, operations: list[dict]) -> dict:
    """
    Modify a drawing: add annotations, dimensions, views, notes, etc.

    operations is a list of BTDrawingModificationRequest objects.
    Each operation has an "action" and type-specific fields.

    Example — add a note:
    [
        {
            "action": "addAnnotation",
            "annotation": {
                "type": "BTANote",
                "text": "Inspect this edge",
                "position": {"x": 100, "y": 50}
            }
        }
    ]
    Returns a modification request ID for status polling.
    """
    result = post(
        f"/api/v10/drawings/d/{did}/w/{wid}/e/{eid}/modify",
        {"jsonRequests": operations},
    )
    return {
        "modificationId": result.get("id", ""),
        "requestState": result.get("requestState", ""),
    }


@mcp.tool()
def get_drawing_modification_status(did: str, wid: str, eid: str, mid: str) -> dict:
    """
    Poll the status of a drawing modification request.

    mid: the modification ID returned by modify_drawing.
    requestState will be one of: ACTIVE, DONE, FAILED.
    """
    return get(f"/api/v10/drawings/d/{did}/w/{wid}/e/{eid}/modify/{mid}")


@mcp.tool()
def export_drawing(
    did: str,
    wid: str,
    eid: str,
    format_name: str = "PDF",
    timeout: int = 120,
) -> str:
    """
    Export a drawing to a file format. Returns the path of the downloaded file.

    format_name: PDF, DXF, DWG, SVG, PNG, JPEG (default: PDF)
    """
    from onshape_mcp.client import download_external_data, poll_translation, post as _post

    suffix_map = {
        "PDF": ".pdf",
        "DXF": ".dxf",
        "DWG": ".dwg",
        "SVG": ".svg",
        "PNG": ".png",
        "JPEG": ".jpg",
    }
    suffix = suffix_map.get(format_name.upper(), ".bin")

    payload = {
        "formatName": format_name.upper(),
        "documentId": did,
        "workspaceId": wid,
        "elementId": eid,
        "storeInDocument": False,
    }
    result = _post(f"/api/v10/drawings/d/{did}/w/{wid}/e/{eid}/translations", payload)
    translation_id = result.get("id", "")
    if not translation_id:
        raise RuntimeError(f"No translation ID returned: {result}")

    done = poll_translation(translation_id, timeout=timeout)
    external_ids = done.get("resultExternalDataIds", [])
    if not external_ids:
        raise RuntimeError("Drawing export completed but no result data returned")

    return download_external_data(did, external_ids[0], suffix=suffix)


@mcp.tool()
def get_drawing_translator_formats(did: str, wid: str, eid: str) -> list[str]:
    """List the available export formats for a drawing element."""
    result = get(f"/api/v10/drawings/d/{did}/w/{wid}/e/{eid}/translatorFormats")
    formats = result if isinstance(result, list) else result.get("formats", [])
    return [f.get("name", f) if isinstance(f, dict) else f for f in formats]
