"""Tool that returns a guide for building 3D geometry via the Onshape API."""

from onshape_mcp.mcp_instance import mcp

_GUIDE = """
# Building 3D Geometry with the Onshape MCP

## Account Constraints

Free-tier Onshape accounts can only create **public** documents.
Always pass `is_public=True` to `create_document` unless you have a paid account.

## Typical Workflow

1. `create_document(name, is_public=True)` → get `id` and `defaultWorkspace`
2. `list_elements(did, wid)` → find the default Part Studio `eid`
3. Add sketch(es) and features via `add_part_studio_feature`
4. Verify with `get_part_studio_mass_properties` or `get_part_studio_body_details`
5. Export with `export_part_studio_step` or `export_part_studio_stl`

---

## Feature JSON Format

All features use a top-level `{"feature": {...}}` wrapper.

### Sketch (BTMSketch-151)

```json
{
  "feature": {
    "btType": "BTMSketch-151",
    "name": "Sketch 1",
    "featureType": "newSketch",
    "namespace": "",
    "suppressed": false,
    "returnAfterSubfeatures": false,
    "subFeatures": [],
    "parameterLibraries": [],
    "parameters": [
      {
        "btType": "BTMParameterQueryList-148",
        "parameterId": "sketchPlane",
        "queries": [{ SEE PLANE QUERIES BELOW }]
      }
    ],
    "entities": [ { SEE ENTITY TYPES BELOW } ],
    "constraints": [ { SEE CONSTRAINTS BELOW } ]
  }
}
```

The response includes `feature.featureId` — save this, it is needed for subsequent features.

### Extrude (BTMFeature-134)

```json
{
  "feature": {
    "btType": "BTMFeature-134",
    "name": "Extrude 1",
    "featureType": "extrude",
    "namespace": "",
    "suppressed": false,
    "returnAfterSubfeatures": false,
    "subFeatures": [],
    "parameterLibraries": [],
    "parameters": [
      {"btType": "BTMParameterEnum-145", "parameterId": "domain",               "value": "MODEL",  "enumName": "OperationDomain",        "namespace": ""},
      {"btType": "BTMParameterEnum-145", "parameterId": "bodyType",             "value": "SOLID",  "enumName": "ExtendedToolBodyType",   "namespace": ""},
      {"btType": "BTMParameterEnum-145", "parameterId": "operationType",        "value": "NEW",    "enumName": "NewBodyOperationType",   "namespace": ""},
      {"btType": "BTMParameterEnum-145", "parameterId": "surfaceOperationType", "value": "NEW",    "enumName": "NewSurfaceOperationType","namespace": ""},
      {
        "btType": "BTMParameterQueryList-148",
        "parameterId": "entities",
        "queries": [
          {
            "btType": "BTMIndividualQuery-138",
            "queryStatement": null,
            "queryString": "query=qSketchRegion(id + \\"SKETCH_FEATURE_ID\\", false);"
          }
        ]
      },
      {"btType": "BTMParameterEnum-145", "parameterId": "endBound", "value": "BLIND", "enumName": "BoundingType", "namespace": ""},
      {
        "btType": "BTMParameterQuantity-147",
        "parameterId": "depth",
        "expression": "21 mm",
        "value": 0.021,
        "isInteger": false,
        "units": "meter"
      }
    ]
  }
}
```

Replace `SKETCH_FEATURE_ID` with the `featureId` returned when you created the sketch.

**operationType values:**
- `"NEW"` — create a new solid body
- `"ADD"` — boolean add (union) with existing bodies
- `"REMOVE"` — boolean subtract (cut)
- `"INTERSECT"` — boolean intersect

**endBound values:**
- `"BLIND"` — extrude by a fixed depth (requires `depth` quantity)
- `"THROUGH_ALL"` — cut through all (still directional — use `oppositeDirection` to flip)

**To flip the extrude direction**, add:
```json
{"btType": "BTMParameterBoolean-144", "parameterId": "oppositeDirection", "value": true}
```
Note: `flipDirection` is **not** the correct parameter — it is silently ignored. Use `oppositeDirection`.

### Fillet (BTMFeature-134, featureType: "fillet")

```json
{
  "feature": {
    "btType": "BTMFeature-134",
    "name": "Fillet 1",
    "featureType": "fillet",
    "namespace": "",
    "suppressed": false,
    "returnAfterSubfeatures": false,
    "subFeatures": [],
    "parameterLibraries": [],
    "parameters": [
      {
        "btType": "BTMParameterQuantity-147",
        "parameterId": "radius",
        "expression": "2 mm",
        "value": 0.002,
        "isInteger": false,
        "units": "meter"
      },
      {
        "btType": "BTMParameterQueryList-148",
        "parameterId": "entities",
        "queries": [
          {
            "btType": "BTMIndividualCreatedByQuery-137",
            "featureId": "EXTRUDE_FEATURE_ID",
            "entityType": "EDGE",
            "bodyType": "SOLID",
            "filterConstruction": false,
            "queryStatement": null,
            "queryString": "query = qCreatedBy(id + \\"EXTRUDE_FEATURE_ID\\", EntityType.EDGE);"
          }
        ]
      }
    ]
  }
}
```

---

## Plane Queries

### Built-in origin planes

```json
{
  "btType": "BTMIndividualQuery-138",
  "queryString": "query=qCompressed(1.0,\\"%B5$QueryM4Sa$entityTypeBa$EntityTypeS4$FACESb$historyTypeS8$CREATIONSb$operationIdB2$IdA1S3.7$TopplaneOpS9$queryTypeS5$DUMMY\\",id);",
  "deterministicIds": ["JDC"]
}
```

The compressed queryString above always selects the **Top** plane (`deterministicId: "JDC"`).
For **Front** use `"FrontplaneOp"` and for **Right** use `"RightplaneOp"` in the queryString
(deterministicIds will differ — inspect via `get_part_studio_features` on any document to confirm).

---

## Sketch Entity Types

### Line segment (BTMSketchCurveSegment-155)

```json
{
  "btType": "BTMSketchCurveSegment-155",
  "entityId": "myLine",
  "startPointId": "myLine.start",
  "endPointId": "myLine.end",
  "centerId": "",
  "index": 1,
  "isConstruction": false,
  "isFromSplineControlPolygon": false,
  "isFromSplineHandle": false,
  "isFromEndpointSplineHandle": false,
  "internalIds": [],
  "curvedTextIds": [],
  "offsetCurveExtensions": [],
  "namespace": "",
  "name": "",
  "parameters": [],
  "geometry": {
    "btType": "BTCurveGeometryLine-117",
    "pntX": 0.0,    "pntY": 0.0,
    "dirX": 1.0,    "dirY": 0.0
  },
  "startParam": 0.0,
  "endParam": 0.01
}
```

**Geometry for a line from (x1,y1) to (x2,y2):**
- `pntX = x1`, `pntY = y1`
- `length = sqrt((x2-x1)² + (y2-y1)²)`
- `dirX = (x2-x1)/length`, `dirY = (y2-y1)/length`
- `startParam = 0`, `endParam = length`
- All coordinates in **metres**

**To create a closed polygon** (e.g. a hexagon), share the `startPointId`/`endPointId`
between adjacent edges — e.g. edge 0 `endPointId="p1"`, edge 1 `startPointId="p1"`.
Onshape recognises shared IDs as coincident points.

### Arc segment (BTMSketchCurveSegment-155 with circle geometry)

```json
{
  "btType": "BTMSketchCurveSegment-155",
  "entityId": "myArc",
  "startPointId": "myArc.start",
  "endPointId": "myArc.end",
  "centerId": "myArc.center",
  "geometry": {
    "btType": "BTCurveGeometryCircle-115",
    "xCenter": 0.0, "yCenter": 0.0,
    "radius": 0.01,
    "xDir": 1.0, "yDir": 0.0,
    "clockwise": false
  },
  "startParam": 0.0,
  "endParam": 1.5707963
}
```

For a full circle `startParam = 0`, `endParam = 2π`.
For an arc, `startParam`/`endParam` are angles in radians from `xDir`.

---

## Constraints (BTMSketchConstraint-2)

```json
{
  "btType": "BTMSketchConstraint-2",
  "constraintType": "COINCIDENT",
  "hasOffsetData1": false, "offsetOrientation1": false, "offsetDistance1": 0.0,
  "hasOffsetData2": false, "offsetOrientation2": false, "offsetDistance2": 0.0,
  "hasPierceParameter": false, "pierceParameter": 0.0,
  "helpParameters": [],
  "namespace": "",
  "name": "",
  "parameters": [],
  "entityId": "myConstraint"
}
```

**Common constraintType values:** `COINCIDENT`, `HORIZONTAL`, `VERTICAL`,
`PERPENDICULAR`, `PARALLEL`, `EQUAL`, `MIDPOINT`, `TANGENT`, `FIX`, `SYMMETRIC`.

For `COINCIDENT`, add `localFirst`/`localSecond` string parameters pointing at the
entity IDs to constrain together.

---

## Useful Patterns

### Hexagonal prism (~10 cm³, FDM printable)

```python
import math

R = 0.0135  # circumradius in metres (edge length = R for regular hexagon)
H = 0.021   # height in metres
# Volume ≈ (3√3/2) * R² * H ≈ 9,943 mm³

verts = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)))
         for a in range(0, 360, 60)]

entities = []
for i in range(6):
    x1, y1 = verts[i]
    x2, y2 = verts[(i + 1) % 6]
    length = math.hypot(x2 - x1, y2 - y1)
    entities.append({
        "btType": "BTMSketchCurveSegment-155",
        "entityId": f"hexEdge{i}",
        "startPointId": f"p{i}",
        "endPointId": f"p{(i + 1) % 6}",
        "centerId": "",
        "index": i + 1,
        "isConstruction": False,
        "isFromSplineControlPolygon": False,
        "isFromSplineHandle": False,
        "isFromEndpointSplineHandle": False,
        "internalIds": [], "curvedTextIds": [], "offsetCurveExtensions": [],
        "namespace": "", "name": "", "parameters": [],
        "geometry": {
            "btType": "BTCurveGeometryLine-117",
            "pntX": x1, "pntY": y1,
            "dirX": (x2 - x1) / length, "dirY": (y2 - y1) / length,
        },
        "startParam": 0.0,
        "endParam": length,
    })
```

---

## Construction Planes (cPlane)

To create a sketch on a plane that doesn't exist yet (e.g. the top face of a prism),
create a construction plane first, then reference it in the sketch.

### Create an offset cPlane

```json
{
  "feature": {
    "btType": "BTMFeature-134",
    "name": "My Plane",
    "featureType": "cPlane",
    "namespace": "", "suppressed": false,
    "returnAfterSubfeatures": false, "subFeatures": [], "parameterLibraries": [],
    "parameters": [
      {"btType": "BTMParameterEnum-145", "parameterId": "cplaneType", "value": "OFFSET", "enumName": "CPlaneType", "namespace": ""},
      {"btType": "BTMParameterQueryList-148", "parameterId": "entities", "queries": [{ TOP PLANE QUERY }]},
      {"btType": "BTMParameterQuantity-147", "parameterId": "offset", "expression": "21 mm", "value": 0.021, "isInteger": false, "units": "meter"}
    ]
  }
}
```

### Reference the cPlane in a sketch

The sketch's `sketchPlane` query uses a compressed queryString. The pattern for a
cPlane with featureId `{ID}` (where `{ID}` is 17 characters long) is:

```
query=qCompressed(1.0,"%B5$QueryM4Sa$entityTypeBa$EntityTypeS4$FACESb$historyTypeS8$CREATIONSb$operationIdB2$IdA1S11.7${ID}planeOpS9$queryTypeS5$DUMMY",id);
```

The `S11` prefix is correct for 17-character feature IDs (all Onshape-generated IDs
that look like `FAxgVH0UsDn5xsH_1`). The built-in Top plane uses `S3.7$TopplaneOp`.

In Python:
```python
cplane_qs = f'query=qCompressed(1.0,"%B5$QueryM4Sa$entityTypeBa$EntityTypeS4$FACESb$historyTypeS8$CREATIONSb$operationIdB2$IdA1S11.7${cplane_fid}planeOpS9$queryTypeS5$DUMMY",id);'
```

---

## Checking Your Work

- `get_part_studio_mass_properties` — volume is in m³; multiply by 1e6 to get cm³
- `get_part_studio_body_details` — lists faces/edges, useful for debugging
- `get_part_studio_features` — returns full feature tree; check `featureStatus: "OK"`
- `featureStatus: "ERROR"` usually means a bad entity query (wrong featureId, wrong
  entity type) or an open/unclosed sketch profile
"""


@mcp.tool()
def get_3d_modelling_guide() -> str:
    """
    Returns a comprehensive guide for building 3D geometry programmatically via this MCP.

    Covers:
    - Account constraints (free vs paid)
    - The sketch → extrude workflow
    - Full BTMFeature JSON format for sketches, extrudes, and fillets
    - Sketch entity types: line segments and arcs
    - Plane queries (Top, Front, Right)
    - Sketch constraints
    - Common patterns (hexagonal prism, closed polygons)
    - How to check and debug features
    """
    return _GUIDE
