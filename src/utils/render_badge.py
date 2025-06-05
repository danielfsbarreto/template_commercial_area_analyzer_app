from models import Execution


def render_badge(execution: Execution):
    return {
        "pending": ":orange-badge[⚠️ Pending]",
        "completed": ":green-badge[✅ Completed]",
    }.get(execution.status)  # type: ignore
