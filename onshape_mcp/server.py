"""Onshape MCP Server — entry point and tool registration."""

from onshape_mcp.mcp_instance import mcp  # noqa: F401 — re-exported for convenience

# Import tool modules to trigger @mcp.tool() registration.
import onshape_mcp.tools.assemblies  # noqa: F401
import onshape_mcp.tools.configurations  # noqa: F401
import onshape_mcp.tools.documents  # noqa: F401
import onshape_mcp.tools.drawings  # noqa: F401
import onshape_mcp.tools.import_export  # noqa: F401
import onshape_mcp.tools.metadata  # noqa: F401
import onshape_mcp.tools.part_studios  # noqa: F401
import onshape_mcp.tools.readme  # noqa: F401


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
