"""Tools for Onshape Part Studio operations."""

from onshape_mcp.client import delete, get, post
from onshape_mcp.mcp_instance import mcp


@mcp.tool()
def create_part_studio(did: str, wid: str, name: str) -> dict:
    """Create a new Part Studio tab in a document workspace."""
    result = post(f"/api/v6/partstudios/d/{did}/w/{wid}", {"name": name})
    return {"id": result.get("id", ""), "name": result.get("name", name)}


@mcp.tool()
def get_part_studio_features(did: str, wid: str, eid: str) -> dict:
    """Get the list of features in a Part Studio."""
    return get(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/features")


@mcp.tool()
def add_part_studio_feature(did: str, wid: str, eid: str, feature: dict) -> dict:
    """
    Add a feature to a Part Studio.

    The feature dict should contain a BTMFeature structure, e.g.:
    {
        "feature": {
            "type": 134,
            "typeName": "BTMFeature",
            "featureType": "cube",
            "name": "My Cube",
            "parameters": [...]
        }
    }
    """
    return post(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/features", feature)


@mcp.tool()
def update_part_studio_feature(did: str, wid: str, eid: str, fid: str, feature: dict) -> dict:
    """Update an existing Part Studio feature by its feature ID."""
    return post(
        f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/features/featureid/{fid}", feature
    )


@mcp.tool()
def delete_part_studio_feature(did: str, wid: str, eid: str, fid: str) -> dict:
    """Delete a feature from a Part Studio by its feature ID."""
    delete(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/features/featureid/{fid}")
    return {"deleted": fid}


@mcp.tool()
def get_part_studio_body_details(did: str, wid: str, eid: str) -> dict:
    """Get geometric body details for all bodies in a Part Studio."""
    return get(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/bodydetails")


@mcp.tool()
def get_part_studio_mass_properties(did: str, wid: str, eid: str) -> dict:
    """Get mass properties (mass, volume, centroid, inertia) for parts in a Part Studio."""
    return get(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/massproperties")


@mcp.tool()
def get_part_studio_bounding_boxes(did: str, wid: str, eid: str) -> dict:
    """Get axis-aligned bounding boxes for all parts in a Part Studio."""
    return get(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/boundingboxes")


@mcp.tool()
def get_parts_in_part_studio(did: str, wid: str, eid: str) -> list[dict]:
    """List all parts in a Part Studio with their IDs and names."""
    result = get(f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/parts")
    parts = result if isinstance(result, list) else result.get("parts", [])
    return [
        {
            "partId": p.get("partId", ""),
            "name": p.get("name", ""),
            "bodyType": p.get("bodyType", ""),
            "isMesh": p.get("isMesh", False),
        }
        for p in parts
    ]
