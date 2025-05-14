from typing import Dict, Any, Tuple, Optional, List, Literal

class StreamlitFlowNode:
    def __init__(
        self,
        id: str,
        pos: Tuple[float, float],
        data: Dict[str, Any],
        node_type: Literal['default', 'input', 'output', 'llm', 'api'] = 'default',
        source_position: Literal['bottom', 'top', 'left', 'right'] = 'bottom',
        target_position: Literal['bottom', 'top', 'left', 'right'] = 'top',
        style: Dict[str, Any] = None,
        draggable: bool = True,
        selectable: bool = True,
        connectable: bool = True
    ):
        self.id = id
        self.pos = pos
        self.data = data
        self.node_type = node_type
        self.source_position = source_position
        self.target_position = target_position
        self.style = style or {}
        self.draggable = draggable
        self.selectable = selectable
        self.connectable = connectable
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'pos': self.pos,
            'data': self.data,
            'node_type': self.node_type,
            'source_position': self.source_position,
            'target_position': self.target_position,
            'style': self.style,
            'draggable': self.draggable,
            'selectable': self.selectable,
            'connectable': self.connectable
        }

class StreamlitFlowEdge:
    def __init__(
        self,
        id: str,
        source: str,
        target: str,
        edge_type: Literal['default', 'straight', 'smoothstep', 'step', 'simplebezier'] = 'default',
        label: str = "",
        animated: bool = False,
        style: Dict[str, Any] = None,
        label_style: Dict[str, Any] = None,
        label_show_bg: bool = True
    ):
        self.id = id
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.label = label
        self.animated = animated
        self.style = style or {}
        self.label_style = label_style or {}
        self.label_show_bg = label_show_bg
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target,
            'edge_type': self.edge_type,
            'label': self.label,
            'animated': self.animated,
            'style': self.style,
            'label_style': self.label_style,
            'label_show_bg': self.label_show_bg
        }