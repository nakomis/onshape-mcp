"""Shared FastMCP instance — imported by all tool modules."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "onshape-mcp",
    instructions=(
        "Before building or editing geometry, call get_3d_modelling_guide — it "
        "returns the BTMFeature JSON reference AND 'Claude's guide to the "
        "Onshape MCP' (docs/claude-guide.md in this repo), which records the "
        "API's silent failure modes: circles never form sketch regions, a "
        "sketch inside existing material yields no region, one sketch with "
        "several loops extrudes only one of them, ADD needs an explicit "
        "booleanScope, and featureStatus OK does not mean the geometry is "
        "right — always verify by exporting and measuring. Add to that file "
        "whenever the API surprises you."
    ),
)
