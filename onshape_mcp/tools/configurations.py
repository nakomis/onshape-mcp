"""Tools for Onshape configuration management."""

from onshape_mcp.client import get, post
from onshape_mcp.mcp_instance import mcp


@mcp.tool()
def get_configuration(did: str, wid: str, eid: str) -> dict:
    """
    Get the configuration definition for a Part Studio or Assembly element.
    Returns the list of configuration inputs and their current values.
    """
    return get(f"/api/v10/elements/d/{did}/w/{wid}/e/{eid}/configuration")


@mcp.tool()
def update_configuration(did: str, wid: str, eid: str, config_data: dict) -> dict:
    """
    Update configuration parameters for a Part Studio or Assembly element.

    config_data should be a BTConfigurationUpdateCall2933 structure, e.g.:
    {
        "configurationParameters": [
            {
                "btType": "BTMConfigurationParameterEnum-105",
                "parameterId": "my_param",
                "parameterValue": "option_a"
            }
        ]
    }
    """
    return post(f"/api/v10/elements/d/{did}/w/{wid}/e/{eid}/configuration", config_data)


@mcp.tool()
def encode_configuration(did: str, eid: str, config_map: list[dict]) -> dict:
    """
    Encode a configuration parameter map into a URL-safe string.

    config_map is a list of parameter value objects, e.g.:
    [{"parameterId": "Width", "parameterValue": "0.05 m"}]

    Returns an encoded configuration string for use in export and other API calls.
    """
    return post(
        f"/api/v10/elements/d/{did}/e/{eid}/configurationencodings",
        {"parameters": config_map},
    )
