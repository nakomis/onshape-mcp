"""Tools for Onshape document management."""

from onshape_mcp.client import delete, get, post
from onshape_mcp.mcp_instance import mcp


@mcp.tool()
def search_documents(
    query: str = "",
    owner_type: int = 1,
    filter: int = 0,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """
    Search for Onshape documents.

    owner_type: 1=user (default), 2=company, 3=team
    filter: 0=all (default), 1=created, 2=shared, 4=public, 6=trash
    """
    params: dict = {"ownerType": owner_type, "filter": filter, "limit": limit, "offset": offset}
    if query:
        params["q"] = query
    result = get("/api/v10/documents", **params)
    items = result.get("items", result) if isinstance(result, dict) else result
    return [
        {
            "id": d["id"],
            "name": d["name"],
            "description": d.get("description", ""),
            "owner": d.get("owner", {}).get("name", ""),
            "createdAt": d.get("createdAt", ""),
            "modifiedAt": d.get("modifiedAt", ""),
            "href": d.get("href", ""),
        }
        for d in items
    ]


@mcp.tool()
def get_document(did: str) -> dict:
    """Get details of a specific document by ID."""
    d = get(f"/api/v10/documents/{did}")
    return {
        "id": d["id"],
        "name": d["name"],
        "description": d.get("description", ""),
        "owner": d.get("owner", {}).get("name", ""),
        "defaultWorkspace": d.get("defaultWorkspace", {}).get("id", ""),
        "createdAt": d.get("createdAt", ""),
        "modifiedAt": d.get("modifiedAt", ""),
        "href": d.get("href", ""),
    }


@mcp.tool()
def create_document(name: str, description: str = "") -> dict:
    """Create a new Onshape document."""
    payload: dict = {"name": name}
    if description:
        payload["description"] = description
    d = post("/api/v10/documents", payload)
    return {"id": d["id"], "name": d["name"], "defaultWorkspace": d.get("defaultWorkspace", {}).get("id", "")}


@mcp.tool()
def update_document(did: str, name: str = "", description: str = "") -> dict:
    """Update a document's name and/or description."""
    payload: dict = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    d = post(f"/api/v10/documents/{did}", payload)
    return {"id": d["id"], "name": d["name"]}


@mcp.tool()
def delete_document(did: str, forever: bool = False) -> dict:
    """
    Delete a document. Set forever=True to permanently delete rather than move to trash.
    """
    delete(f"/api/v10/documents/{did}", forever=str(forever).lower())
    return {"deleted": did}


@mcp.tool()
def list_elements(did: str, wid: str) -> list[dict]:
    """List all elements (tabs) within a document workspace."""
    elements = get(f"/api/v10/documents/d/{did}/w/{wid}/elements")
    return [
        {
            "id": e["id"],
            "name": e["name"],
            "elementType": e.get("elementType", ""),
            "dataType": e.get("dataType", ""),
            "lengthUnits": e.get("lengthUnits", ""),
        }
        for e in (elements if isinstance(elements, list) else [])
    ]


@mcp.tool()
def create_version(did: str, wid: str, name: str, description: str = "") -> dict:
    """Create a named version of a document from the current workspace state."""
    payload: dict = {"documentId": did, "workspaceId": wid, "name": name}
    if description:
        payload["description"] = description
    v = post(f"/api/v10/documents/d/{did}/versions", payload)
    return {"id": v["id"], "name": v["name"], "createdAt": v.get("createdAt", "")}


@mcp.tool()
def list_versions(did: str) -> list[dict]:
    """List all versions of a document."""
    result = get(f"/api/v10/documents/d/{did}/versions")
    versions = result if isinstance(result, list) else result.get("items", [])
    return [
        {"id": v["id"], "name": v["name"], "createdAt": v.get("createdAt", "")}
        for v in versions
    ]


@mcp.tool()
def list_workspaces(did: str) -> list[dict]:
    """List all workspaces in a document."""
    result = get(f"/api/v10/documents/d/{did}/workspaces")
    workspaces = result if isinstance(result, list) else result.get("items", [])
    return [
        {"id": w["id"], "name": w["name"], "isReadOnly": w.get("isReadOnly", False)}
        for w in workspaces
    ]
