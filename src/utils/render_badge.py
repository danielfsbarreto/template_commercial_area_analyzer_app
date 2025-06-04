from models import Execution


def render_badge(execution: Execution):
    return {
        "pending": {
            "label": "Pending",
            "icon": ":material/schedule:",
            "color": "orange",
        },
        "completed": {
            "label": "Completed",
            "icon": ":material/check:",
            "color": "green",
        },
    }.get(execution.status)  # type: ignore
