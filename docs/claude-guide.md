# Claude's guide to the Onshape MCP

Hard-won notes from driving this server. **Read this before building geometry** —
`get_3d_modelling_guide` covers the JSON shapes; this covers what the API does
that the guide does not warn you about.

Keep it current: add a line whenever something surprises you.

## The rule that matters most

**`featureStatus: "OK"` does not mean the geometry is what you asked for.**
Verify every part by exporting an STL and measuring it, or with
`get_part_studio_mass_properties` (volume in m³ × 1e9 = mm³). Two failures in
one session were silent: an extrude that quietly used one of two profiles, and
a hole that never appeared. Both reported OK.

Arithmetic on the expected volume catches this quickly: compute what the part
*should* weigh in mm³ before you look at the number.

## Sketch regions — where the traps are

`qSketchRegion(id + "FEATURE_ID", filterInnerLoops)` is the query every extrude
uses, and it is the single biggest source of silent failure.

- **Full circles never produce a region** through this API. A
  `BTCurveGeometryCircle-115` with `startParam: 0, endParam: 2π` is accepted,
  the sketch reports OK, and the extrude comes back `ERROR` with
  `deterministicIds: []`. Tried with and without `startPointId`/`endPointId`,
  and with an explicit `BTMSketchPoint-158` centre. **Use a polygon of line
  segments instead** — an octagon is fine for a peg or a screw hole, and for a
  clearance hole you size it across corners.
- **A sketch whose profile sits inside existing material often yields no
  region.** Sketch a hole on a plane that is already buried in a solid and the
  extrude gets an empty query. Draw the hole as an **inner loop of the same
  sketch as its parent profile**, or sketch it before the material exists.
- **One sketch, several separate closed loops = only one region comes back.**
  Two octagons in one sketch extruded a single peg and no error. Put each
  separate solid profile in its **own sketch**.
- **Inner loops need `filterInnerLoops: true`** or the extrude fills the hole
  in: `false` returned two regions (ring + disc) and produced a solid slab.
  With `true` you get one region — but *verify*: in one case the region count
  was right and the hole still did not appear in the exported mesh.
- **When a hole refuses to appear, redesign it as an open slot.** A U-slot cut
  into the outline is a single closed loop with no inner loop at all, so none
  of the above can bite. On a bracket it is often the better part anyway (the
  screw slides in without being removed).

## Plane queries

Compressed query strings, `S<n>` is the length of the plane's name:

| Plane | queryString fragment | deterministicIds |
|---|---|---|
| Top | `...IdA1S3.7$TopplaneOp...` | `["JDC"]` |
| Front | `...IdA1S5.7$FrontplaneOp...` | (resolves on its own) |
| Right | `...IdA1S5.7$RightplaneOp...` | (untested) |
| cPlane | `...IdA1S11.7${17-char featureId}planeOp...` | (resolves on its own) |

A cPlane query that comes back with `deterministicIds: []` means the plane did
not resolve — check the feature id is exactly 17 characters.

## Extrude direction

`oppositeDirection` is the only flag that works (`flipDirection` is accepted
and ignored). Which way "opposite" points depends on the plane, and it is not
what you would guess:

- **Top plane:** `true` extrudes **down** (−Z).
- **Front plane:** `true` extrudes **+Y**, `false` extrudes **−Y**.

Always confirm by exporting and checking the bounding box; a part built on the
wrong side of a plane still reports OK.

## Make cuts robust

Cuts written against today's geometry break silently when that geometry moves,
and the feature still reports OK.

- **Use `endBound: "THROUGH_ALL"` (or `"UP_TO_NEXT"`) for cuts**, not `BLIND`
  with a measured depth. This is the native Onshape habit and it survives a
  part getting thicker or moving.
- **Oversize the cut profile in-plane too.** Through All only governs the
  extrude direction; a sketch rectangle sized to the current thickness will
  under-cut as soon as that thickness changes. Run the profile well past the
  material on both sides.
- After moving any body, re-check every feature that referenced its old
  position. Moving a post 3.2mm outboard left a slot cut behind: the slot
  stopped 2mm short of the outer face, so the screw could not pass, and
  nothing reported an error.

## Booleans

- **`featureType: "boolean"` is rejected with HTTP 400** in the shape the docs
  suggest. Do not bother; use an extrude with `operationType: "ADD"` instead.
- **`ADD` with `defaultScope: true` can fail with `ERROR`** even when the new
  material clearly touches an existing body. Setting `defaultScope: false` and
  naming the target in `booleanScope` works:

  ```json
  {"btType": "BTMParameterBoolean-144", "parameterId": "defaultScope", "value": false},
  {"btType": "BTMParameterQueryList-148", "parameterId": "booleanScope", "queries": [
    {"btType": "BTMIndividualCreatedByQuery-137", "featureId": "FExtrude_1",
     "entityType": "BODY", "bodyType": "SOLID", "filterConstruction": false,
     "queryStatement": null,
     "queryString": "query = qCreatedBy(id + \"FExtrude_1\", EntityType.BODY);"}]}
  ```

## Exports

- Export endpoints answer **307** to a regional host (`cad-euw1.onshape.com`).
  The client follows it and **re-signs** for the redirect target: the HMAC
  covers path and query, so replaying the original header gives 401. See
  `client._request`.
- `export_part_studio_stl` groups all bodies into one `solid Mesh` block, so
  measuring a single part from a multi-body studio means filtering by
  coordinates. Export per part with `part_id` when you need them separately.

## Verifying assemblies, not just parts

Measuring one part is not enough: parts can be individually correct and still
wrong together. A slot cut in one body ran directly under the wall of the body
that stands on it, leaving the wall overhanging fresh air — every feature
reported OK and every dimension was as drawn. Compare footprints between
bodies (project each to x/y and check overlaps) and walk the moving part
through its full travel looking for collisions with the fixed one.

The human spotted this one by looking at the model. Ask for a look when the
geometry is an assembly.

## Verifying without eyes

- `get_part_studio_bounding_boxes` — overall extent, cheap sanity check.
- `get_part_studio_mass_properties` — `volume` in m³; compare against hand
  arithmetic.
- Export STL and parse it (the files are ASCII: lines starting `vertex`).
  Cluster vertices by z to confirm each feature landed where intended.

## Endpoints that are wrong in this server

- `get_parts_in_part_studio` called `/partstudios/{d}/{w}/{e}/parts` → **404**.
  Parts live at `/api/v6/parts/d/{did}/w/{wid}/e/{eid}` (fixed).

## Housekeeping

- Free-tier accounts can only create **public** documents: pass
  `is_public=True` to `create_document`.
- `create_document` → `list_elements` for the Part Studio `eid`.
- Failed features stay in the tree as errors; delete them
  (`delete_part_studio_feature`) or the next export inherits the mess.
- Deleting a feature that a later feature references (a `booleanScope`, say)
  breaks that feature — delete in reverse order.
