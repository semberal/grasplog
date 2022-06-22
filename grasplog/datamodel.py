import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, ClassVar

from grasplog.json_output import LogEventJson, ClusteringJson, ClusterInfoJson, NoisyEventsJson
from grasplog.ui_helper import print_msg
from grasplog.util import Timer


class OutputFormat(Enum):
    pretty_format = "pretty"
    json_format = "json"

    def __str__(self) -> str:
        return self.value


@dataclass
class AppContext:
    path_glob: str
    max_distance: float
    max_samples_per_cluster: int
    max_noisy_samples: int
    output_format: OutputFormat
    debug_mode: bool
    DEFAULT_MAX_DISTANCE: ClassVar[float] = 2.1


@dataclass
class LogEvent:
    line_nr: int
    message: str

    def to_json(self) -> LogEventJson:
        return LogEventJson(self.line_nr, self.message)


@dataclass
class ClusterInfo:
    cluster_id: int
    total_event_count: int
    samples: List[LogEvent]

    def to_cluster_json(self) -> ClusterInfoJson:
        return ClusterInfoJson(self.cluster_id, [x.to_json() for x in self.samples], self.total_event_count)

    def to_noisy_events_json(self) -> NoisyEventsJson:
        return NoisyEventsJson([x.to_json() for x in self.samples], self.total_event_count)


class ClusteringAccumulator:
    def __init__(self, max_samples_per_cluster: int, max_noisy_samples: int):
        self.clusters: Dict[int, ClusterInfo] = {}
        self.noisy_events: ClusterInfo = ClusterInfo(-1, 0, [])
        self.__max_samples_per_cluster = max_samples_per_cluster
        self.__max_noisy_samples = max_noisy_samples

    def report_event(self, cluster_id: int, event: LogEvent) -> None:
        cluster = self.clusters.get(cluster_id)
        if cluster is None:
            self.clusters[cluster_id] = ClusterInfo(cluster_id, 1, [event])
        else:
            cluster.total_event_count += 1
            if len(cluster.samples) < self.__max_samples_per_cluster:
                cluster.samples.append(event)

    def report_noisy_event(self, event: LogEvent) -> None:
        self.noisy_events.total_event_count += 1
        if self.noisy_events.total_event_count < self.__max_noisy_samples:
            self.noisy_events.samples.append(event)

    def output(self, output_format: OutputFormat):
        if output_format == OutputFormat.pretty_format:
            self.__output_human_readable()
        elif output_format == OutputFormat.json_format:
            self.__output_json()

    @staticmethod
    def __output_human_readable_event(event: LogEvent):
        print_msg(f"\tL#{event.line_nr}: {event.message}")

    def __output_human_readable(self) -> None:
        categorized_events_count = sum([y.total_event_count for _, y in self.clusters.items()])
        noisy_events_count = self.noisy_events.total_event_count
        total_events_count = categorized_events_count + noisy_events_count
        categorized_events_perc = categorized_events_count / total_events_count * 100

        for cluster_id, cluster_info in self.clusters.items():
            print_msg(f"Detected cluster {cluster_id}")
            for example in cluster_info.samples:
                self.__output_human_readable_event(example)
            missing_count = cluster_info.total_event_count - self.__max_samples_per_cluster
            if missing_count > 0:
                print_msg(
                    f"\t(...and {missing_count} more similar event(s)...)"
                )
            print_msg("")
        if self.noisy_events.total_event_count > 0:
            print_msg("Noisy events (not belonging to any cluster)")
            for example in self.noisy_events.samples:
                self.__output_human_readable_event(example)
            missing_count = self.noisy_events.total_event_count - self.__max_noisy_samples
            if missing_count > 0:
                print_msg(
                    f"\t(...and {missing_count} more event(s)...)"
                )

        print_msg("")
        print_msg("---")
        print_msg("")
        print_msg(f"Detected clusters: {len(self.clusters)}")
        print_msg(f"Total events: {categorized_events_count + noisy_events_count}")
        print_msg(f"Noisy events: {self.noisy_events.total_event_count}")
        print_msg(f"Categorized events: {categorized_events_count} ({categorized_events_perc:.2f}%)")

    def __output_json(self) -> None:
        result = ClusteringJson(
            clusters=[x.to_cluster_json() for x in self.clusters.values()],
            noisySamples=self.noisy_events.to_noisy_events_json()
        )
        result_dict = asdict(result)
        print_msg(json.dumps(result_dict, indent=2))
