from langgraph.graph import END, START, StateGraph

from app.graph.nodes import generate_node, retrieve_node
from app.graph.state import GraphState


builder = StateGraph(GraphState)

builder.add_node(
    "retrieve",
    retrieve_node,
)

builder.add_node(
    "generate",
    generate_node,
)

builder.add_edge(
    START,
    "retrieve",
)

builder.add_edge(
    "retrieve",
    "generate",
)

builder.add_edge(
    "generate",
    END,
)

graph = builder.compile()