from functools import lru_cache
from mcp.server import MCPServer
from app.core import Clinic

server = MCPServer(
    "ClinicFlow availability",
    instructions="Tools are read-only. Present a slot proposal; the patient confirms in the separate booking UI.",
)


@lru_cache
def service():
    return Clinic()


@server.tool()
def available_appointments() -> list[dict]:
    """List synthetic clinic appointments; never book from model output alone."""
    return [s for s in service().slots() if s["available"]]


@server.tool()
def propose_appointment(slot_id: str) -> dict:
    """Validate an available slot and return a proposal needing human confirmation."""
    slots = {s["id"]: s for s in service().slots() if s["available"]}
    if slot_id not in slots:
        raise ValueError("slot unavailable")
    return dict(slot=slots[slot_id], requires_confirmation=True)


if __name__ == "__main__":
    server.run()
