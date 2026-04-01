"""Tools for Onshape metadata operations."""

from onshape_mcp.client import get, post
from onshape_mcp.mcp_instance import mcp


@mcp.tool()
def get_part_metadata(did: str, wid: str, eid: str, pid: str) -> dict:
    """
    Get metadata properties for a specific part.

    pid: the part ID (e.g. 'JHD' — from get_parts_in_part_studio)
    """
    return get(f"/api/v10/metadata/d/{did}/w/{wid}/e/{eid}/p/{pid}")


@mcp.tool()
def update_part_metadata(did: str, wid: str, eid: str, pid: str, properties: list[dict]) -> dict:
    """
    Update metadata properties for a specific part.

    properties is a list of property objects, e.g.:
    [{"propertyId": "57f3fb8efa3416c06701d60d", "value": "My Part Name"}]

    Common property IDs:
    - name: 57f3fb8efa3416c06701d60d
    - partNumber: 57f3fb8efa3416c06701d60e
    - description: 57f3fb8efa3416c06701d60f
    """
    return post(
        f"/api/v10/metadata/d/{did}/w/{wid}/e/{eid}/p/{pid}",
        {"properties": properties},
    )


@mcp.tool()
def get_element_metadata(did: str, wid: str, eid: str) -> dict:
    """Get metadata properties for a document element (tab)."""
    return get(f"/api/v10/metadata/d/{did}/w/{wid}/e/{eid}")


@mcp.tool()
def update_element_metadata(did: str, wid: str, eid: str, properties: list[dict]) -> dict:
    """
    Update metadata properties for a document element (tab).

    properties is a list of property objects, e.g.:
    [{"propertyId": "...", "value": "New Tab Name"}]
    """
    return post(
        f"/api/v10/metadata/d/{did}/w/{wid}/e/{eid}",
        {"properties": properties},
    )


@mcp.tool()
def get_document_metadata(did: str, wid: str) -> dict:
    """Get metadata for an entire document workspace."""
    return get(f"/api/v10/metadata/d/{did}/w/{wid}")


@mcp.tool()
def update_document_metadata(did: str, wid: str, properties: list[dict]) -> dict:
    """
    Update metadata for an entire document workspace.

    properties is a list of property objects.
    """
    return post(f"/api/v10/metadata/d/{did}/w/{wid}", {"properties": properties})
