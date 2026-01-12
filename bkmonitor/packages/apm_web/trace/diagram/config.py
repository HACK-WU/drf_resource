from dataclasses import dataclass
from typing import Optional

from apm_web.trace.diagram.base import TreeBuildingConfig
from django.conf import settings


@dataclass
class DiagramConfig:

    tree_building_config: TreeBuildingConfig

    @classmethod
    def from_raw(cls, raw_config: dict) -> "DiagramConfig":
        return cls(tree_building_config=TreeBuildingConfig(**raw_config["tree_building_config"]))


@dataclass
class DiagramConfigController:

    flamegraph: DiagramConfig | None = None
    sequence: DiagramConfig | None = None
    topo: DiagramConfig | None = None
    statistics: DiagramConfig | None = None

    @classmethod
    def read(cls, forced_config: dict | None = None) -> Optional["DiagramConfigController"]:
        raw_config = forced_config or settings.APM_TRACE_DIAGRAM_CONFIG
        if not raw_config:
            return None

        controller = cls()

        for key in ["flamegraph", "sequence", "topo", "statistics"]:
            if key in raw_config:
                setattr(controller, key, DiagramConfig.from_raw(raw_config[key]))

        return controller
