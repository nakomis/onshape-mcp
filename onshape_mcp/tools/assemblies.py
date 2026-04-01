"""Tools for Onshape Assembly operations."""

from onshape_mcp.client import delete, get, post
from onshape_mcp.mcp_instance import mcp


@mcp.tool()
def create_assembly(did: str, wid: str, name: str) -> dict:
    """Create a new Assembly tab in a document workspace."""
    result = post(f"/api/v5/assemblies/d/{did}/w/{wid}", {"name": name})
    return {"id": result.get("id", ""), "name": result.get("name", name)}


@mcp.tool()
def get_assembly_definition(
    did: str,
    wid: str,
    eid: str,
    include_mate_features: bool = False,
    include_non_solids: bool = False,
) -> dict:
    """
    Get the full definition of an assembly, including instances and occurrences.

    include_mate_features: include mate feature data in the response
    include_non_solids: include non-solid bodies (surfaces, wireframes, etc.)
    """
    return get(
        f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}",
        includeMateFeatures=str(include_mate_features).lower(),
        includeNonSolids=str(include_non_solids).lower(),
    )


@mcp.tool()
def create_assembly_instance(
    did: str,
    wid: str,
    eid: str,
    instance: dict,
) -> dict:
    """
    Insert an instance into an assembly.

    The instance dict specifies what to insert, e.g.:
    {
        "documentId": "...",
        "elementId": "...",
        "partId": "...",          # for a part
        "isAssembly": false,
        "isWholePartStudio": false,
        "configuration": "default"
    }
    """
    return post(f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}/instances", instance)


@mcp.tool()
def delete_assembly_instance(did: str, wid: str, eid: str, node_id: str) -> dict:
    """Delete an instance from an assembly by its node ID."""
    delete(f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}/instance/nodeid/{node_id}")
    return {"deleted": node_id}


@mcp.tool()
def modify_assembly(did: str, wid: str, eid: str, modifications: dict) -> dict:
    """
    Modify an assembly — apply transforms, suppress/unsuppress instances, delete items.

    modifications is a BTAssemblyModificationParams structure, e.g.:
    {
        "suppressedIdList": ["node_id_1"],
        "transformGroupList": [
            {
                "occurrences": [{"path": ["node_id_1"]}],
                "transform": [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
            }
        ]
    }
    """
    return post(f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}/modify", modifications)


@mcp.tool()
def delete_assembly_feature(did: str, wid: str, eid: str, fid: str) -> dict:
    """Delete a feature (e.g. a mate) from an assembly by its feature ID."""
    delete(f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}/features/featureid/{fid}")
    return {"deleted": fid}


@mcp.tool()
def get_assembly_features(did: str, wid: str, eid: str) -> dict:
    """Get all features (mates, mate connectors, etc.) defined in an assembly."""
    return get(f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}/features")


@mcp.tool()
def get_assembly_mass_properties(did: str, wid: str, eid: str) -> dict:
    """Get mass properties for an assembly."""
    return get(f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}/massproperties")


@mcp.tool()
def get_assembly_bounding_boxes(did: str, wid: str, eid: str) -> dict:
    """Get bounding boxes for all parts in an assembly."""
    return get(f"/api/v5/assemblies/d/{did}/w/{wid}/e/{eid}/boundingboxes")
