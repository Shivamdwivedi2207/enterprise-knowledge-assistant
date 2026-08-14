from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    calendar_action_node,
    email_action_node,
    history_node,
    multi_action_node,
    notion_action_node,
    planner_node,
    retrieve_node,
    route_node,
    select_planning_mode,
)
from app.graph.state import GraphState


def select_route(
    state: GraphState,
) -> str:
    """
    Select the correct LangGraph branch
    based on Gemini's selected action.
    """

    route = state.get(
        "route",
        "rag",
    )

    # =====================================================
    # Gmail
    # =====================================================

    if route in {
        "send_email",
        "email_missing_details",
    }:
        return "email"

    # =====================================================
    # Calendar
    # =====================================================

    if route in {
        "create_calendar_event",
        "calendar_missing_details",
    }:
        return "calendar"

    # =====================================================
    # Notion
    # =====================================================

    if route in {
        "save_chat",
        "save_summary",
        "create_task",
        "meeting_notes",
        "save_insight",
        "project_review",
        "notion_missing_details",
    }:
        return "notion"

    # =====================================================
    # Default → RAG
    # =====================================================

    return "rag"


# =========================================================
# Build Graph
# =========================================================

builder = StateGraph(GraphState)


# =========================================================
# Nodes
# =========================================================
builder.add_node(
    "multi_action",
    multi_action_node,
)

builder.add_node(
    "history",
    history_node,
)

builder.add_node(
    "planner",
    planner_node,
)

builder.add_node(
    "route",
    route_node,
)

builder.add_node(
    "retrieve",
    retrieve_node,
)

builder.add_node(
    "email_action",
    email_action_node,
)

builder.add_node(
    "calendar_action",
    calendar_action_node,
)

builder.add_node(
    "notion_action",
    notion_action_node,
)


# =========================================================
# Main Flow
# =========================================================

builder.add_edge(
    START,
    "history",
)

builder.add_edge(
    "history",
    "planner",
)


# =========================================================
# Planner Routing
# =========================================================

builder.add_conditional_edges(
    "planner",
    select_planning_mode,
    {
        "single": "route",
        "multi": "multi_action",
    },
)


# =========================================================
# Action Routing
# =========================================================

builder.add_conditional_edges(
    "route",
    select_route,
    {
        "rag": "retrieve",
        "email": "email_action",
        "calendar": "calendar_action",
        "notion": "notion_action",
    },
)


# =========================================================
# End Edges
# =========================================================

builder.add_edge(
    "retrieve",
    END,
)

builder.add_edge(
    "email_action",
    END,
)

builder.add_edge(
    "calendar_action",
    END,
)

builder.add_edge(
    "notion_action",
    END,
)

builder.add_edge(
    "multi_action",
    END,
)


# =========================================================
# Compile Graph
# =========================================================

graph = builder.compile()