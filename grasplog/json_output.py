import json
from dataclasses import dataclass, asdict
from typing import List


# These classes represent user-facing API and must remain backward compatible.
@dataclass
class LogEventJson:
    lineNumber: int
    event: str


@dataclass
class ClusterInfoJson:
    id: int
    samples: List[LogEventJson]
    totalCount: int


@dataclass
class NoisyEventsJson:
    samples: List[LogEventJson]
    totalCount: int


@dataclass
class ClusteringJson:
    clusters: List[ClusterInfoJson]
    noisySamples: NoisyEventsJson


def serialize(output: ClusteringJson) -> str:
    d = asdict(output)
    result = json.dumps(d, indent=2)
    return result
