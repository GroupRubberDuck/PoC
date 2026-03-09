from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Result(Enum):
    """Enum per il risultato dei requisiti."""

    PASS = 1
    FAIL = 2
    NA = 3

    def to_node(self) -> Node:
        return Node(self.name, "", None, None)

    def __str__(self) -> str:
        return f"{self.name}"


@dataclass
class Node:
    """Classe per rappresentare un nodo (o domanda) del decision tree"""

    name: str
    question: str
    yes_child: Optional[Node | Result]
    no_child: Optional[Node | Result]


"""Include i decision tree per i diversi requisiti. Ad ogni requisito 
(chiave) corrisponde il rispettivo decision tree."""
DECISION_TREE: dict[str, Node] = {
    "ACM-1": Node(
        "DN-1",
        "Is the public accessibility of the asset the equipment's intended equipment functionality?",
        Result.NA,
        Node(
            "DN-2",
            "Do the physical or logistical measures in the targeted operational enviroment limit the accessibility to authorized entities?",
            Result.NA,
            Node(
                "DN-3",
                "Do legal implications not allow access control mechanisms?",
                Result.NA,
                Node(
                    "DN-4",
                    "Are there access control mechanisms that manage entities' access to the security assets and network assets?",
                    Result.PASS,
                    Result.FAIL,
                ),
            ),
        ),
    ),
    "ACM-2": Node(
        "DN-1",
        "Do the access control mechanisms ensure that only authorized entities have access to the protected security asset or network asset?",
        Result.PASS,
        Result.FAIL,
    ),
}
