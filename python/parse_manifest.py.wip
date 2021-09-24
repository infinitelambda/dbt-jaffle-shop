import json
from typing import Dict, List, Optional
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, validator


class DbtResourceType(str, Enum):
    model = 'model'
    analysis = 'analysis'
    test = 'test'
    operation = 'operation'
    seed = 'seed'
    source = 'source'


class DbtMaterializationType(str, Enum):
    table = 'table'
    view = 'view'
    incremental = 'incremental'
    ephemeral = 'ephemeral'
    seed = 'seed'
    materialized = 'materialzed'


class NodeDeps(BaseModel):
    nodes: List[str]


class NodeConfig(BaseModel):
    materialized: Optional[DbtMaterializationType]


class Node(BaseModel):
    unique_id: str
    path: Path
    resource_type: DbtResourceType
    description: str
    depends_on: Optional[NodeDeps]
    config: NodeConfig


class Manifest(BaseModel):
    nodes: Dict["str", Node]
    sources: Dict["str", Node]

    @validator('nodes', 'sources')
    def filter(cls, val):
        return {k: v for k, v in val.items() if v.resource_type.value in ('model', 'seed', 'source')}


if __name__ == "__main__":
    with open("../target/manifest.json") as fh:
        data = json.load(fh)

    m = Manifest(**data)
    print(m)