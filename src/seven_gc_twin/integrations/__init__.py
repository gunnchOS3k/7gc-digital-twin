"""Cross-repo integration maps."""
from .ai_ran import integration_status as ai_ran_status
from .beam_selection import integration_status as beam_status
from .device_os import integration_status as device_os_status
from .edge_io import integration_status as edge_io_status
from .ntn import integration_status as ntn_status
from .waike import integration_status as waike_status

INTEGRATORS = {
    "edge_io": edge_io_status,
    "ntn": ntn_status,
    "waike": waike_status,
    "device_os": device_os_status,
    "ai_ran": ai_ran_status,
    "beam_selection": beam_status,
}


def integration_map(site_id: str) -> dict:
    return {name: fn(site_id) for name, fn in INTEGRATORS.items()}
