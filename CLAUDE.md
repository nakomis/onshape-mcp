# onshape-mcp

MCP server for the Onshape CAD API. 51 tools across Documents, Part Studios,
Assemblies, Metadata, Configurations, Import/Export, and Drawings.

## Account Constraints

Free-tier Onshape accounts **cannot create private documents**. Always use
`create_document(name, is_public=True)` unless Martin has upgraded his account.

## Building 3D Geometry

Use `get_3d_modelling_guide()` — it returns comprehensive documentation covering
the full BTMFeature JSON format, sketch entity types, plane queries, constraints,
and common patterns. Read it before attempting any Part Studio feature work.

### Key lessons from first use

**Feature API version**: Part Studios use `/api/v6/partstudios/...` (not v10).

**Sketch plane (Top)**: Use this exact query to reference the built-in Top plane:
```json
{
  "btType": "BTMIndividualQuery-138",
  "queryString": "query=qCompressed(1.0,\"%B5$QueryM4Sa$entityTypeBa$EntityTypeS4$FACESb$historyTypeS8$CREATIONSb$operationIdB2$IdA1S3.7$TopplaneOpS9$queryTypeS5$DUMMY\",id);",
  "deterministicIds": ["JDC"]
}
```

**Extrude entities (sketch region)**: Use `qSketchRegion` with the sketch featureId:
```json
{
  "btType": "BTMIndividualQuery-138",
  "queryStatement": null,
  "queryString": "query=qSketchRegion(id + \"SKETCH_FEATURE_ID\", false);"
}
```
The `BTMIndividualCreatedByQuery-137` approach does NOT work for sketch face/region
selection in extrudes — use `BTMIndividualQuery-138` with the `qSketchRegion` queryString.

**Closed polygon**: Share `startPointId`/`endPointId` strings between adjacent edges
(e.g. edge 0 `endPointId="p1"`, edge 1 `startPointId="p1"`). No explicit COINCIDENT
constraints are needed — Onshape recognises shared point IDs automatically.

**Flipping extrude direction**: Use `oppositeDirection: true`, NOT `flipDirection: true`. The `flipDirection` parameter is silently accepted by the API but has no effect. `oppositeDirection` is what the Onshape UI's double-arrow "Flip Direction" button sets.

**Feature status check**: The response includes `featureState.featureStatus`.
`"OK"` means success; `"ERROR"` means something is wrong. Always check this.

**Units**: All coordinates and dimensions are in **metres** in the API. Convert mm → m.

## Package Structure

```
onshape_mcp/
├── client.py          # HMAC-SHA256 signing + HTTP helpers
├── mcp_instance.py    # Shared FastMCP instance
├── server.py          # Entry point — imports all tool modules
└── tools/
    ├── assemblies.py
    ├── configurations.py
    ├── documents.py
    ├── drawings.py
    ├── import_export.py
    ├── metadata.py
    ├── part_studios.py
    └── readme.py      # get_3d_modelling_guide() tool
```

## Credentials

Stored in macOS Keychain, service `"onshape"`:
- `security find-generic-password -s "onshape" -a "access-key" -w`
- `security find-generic-password -s "onshape" -a "secret-key" -w`

The client tries env vars `ONSHAPE_ACCESS_KEY` / `ONSHAPE_SECRET_KEY` first,
then falls back to Keychain automatically.
