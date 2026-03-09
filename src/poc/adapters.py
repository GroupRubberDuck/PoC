from typing import Any

from .dt import Node


class D3JSNodeAdapter:
    """Classe adapter per trasformare la rappresentazione di Python
    del decision tree in rappresentazione per la libreria frontend D3JS"""

    node: Node
    choices: dict[str, bool]

    def __init__(self, node: Node, choices: dict[str, bool]) -> None:
        self.node = node
        self.choices = choices

    def _internal_asdict(self, type: str, edge: str, disabled: bool) -> dict[str, Any]:
        """Metodo ricorsivo che traforma il nodo di questa classe e i suoi figli in `dict`"""
        children: list[dict[str, Any]] = []

        if self.node.yes_child is not None:
            children.append(
                D3JSNodeAdapter(self.node.yes_child, self.choices)._internal_asdict(
                    "internal",
                    "Yes",
                    disabled or not self.choices.get(self.node.name, False),
                )
                if isinstance(self.node.yes_child, Node)
                else D3JSNodeAdapter(
                    self.node.yes_child.to_node(), self.choices
                )._internal_asdict(
                    "leaf-" + str(self.node.yes_child).lower(),
                    "Yes",
                    disabled or not self.choices.get(self.node.name, False),
                )
            )

        if self.node.no_child is not None:
            children.append(
                D3JSNodeAdapter(self.node.no_child, self.choices)._internal_asdict(
                    "internal", "No", disabled or self.choices.get(self.node.name, True)
                )
                if isinstance(self.node.no_child, Node)
                else D3JSNodeAdapter(
                    self.node.no_child.to_node(), self.choices
                )._internal_asdict(
                    "leaf-" + str(self.node.no_child).lower(),
                    "No",
                    disabled or self.choices.get(self.node.name, True),
                )
            )

        result: dict[str, Any] = {
            "name": self.node.name,
            "desc": self.node.question,
            "type": type,
            "edge": edge,
            "disabled": disabled,
        }

        if len(children) > 0:
            result["children"] = children

        return result

    def asdict(self) -> dict[str, Any]:
        """Ritorna questo oggetto come `dict`"""
        return self._internal_asdict("root", "", False)
