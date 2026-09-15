# onshape-mcp

MCP server for the [Onshape](https://www.onshape.com) CAD API. Gives Claude 51 tools spanning Documents, Part Studios, Assemblies, Metadata, Configurations, Import/Export, and Drawings — so you can design, inspect, and export 3D models conversationally.

## Support

If you find this useful, please consider buying me a coffee:

[![Donate with PayPal](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif)](https://www.paypal.com/donate?hosted_button_id=Q3BESC73EWVNN&custom=onshape-mcp)

## Tools

| Category | Examples |
|---|---|
| Documents | create, search, list versions, get metadata |
| Part Studios | add features, get body details, export STL/STEP/Parasolid |
| Assemblies | create instances, modify, export glTF/OBJ/STEP |
| Metadata | get/update part and element metadata |
| Configurations | get/update/encode configurations |
| Import/Export | import files, export drawings |
| Drawings | create, modify, export |

## Installation

```bash
uv pip install -e .
```

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "onshape": {
      "command": "uv",
      "args": ["run", "python", "-m", "onshape_mcp.server"]
    }
  }
}
```

## Credentials

Store your Onshape API keys in macOS Keychain:

```bash
security add-generic-password -s "onshape" -a "access-key" -w "<your-access-key>"
security add-generic-password -s "onshape" -a "secret-key" -w "<your-secret-key>"
```

Or set environment variables `ONSHAPE_ACCESS_KEY` / `ONSHAPE_SECRET_KEY`.

## Licence

[CC0 1.0 Universal](LICENSE) — public domain.
