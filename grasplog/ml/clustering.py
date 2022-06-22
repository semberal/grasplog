import logging
from typing import Iterator

from nltk.tokenize import wordpunct_tokenize  # type:ignore
from nltk.util import ngrams  # type:ignore
from sklearn.cluster import DBSCAN, OPTICS  # type:ignore
from sklearn.feature_extraction import FeatureHasher  # type:ignore
from sklearn.feature_extraction import FeatureHasher  # type:ignore
from sklearn.pipeline import Pipeline  # type:ignore

from grasplog.datamodel import ClusteringAccumulator, LogEvent
from grasplog.ml.text_processing import DEFAULT_ANALYZER
from grasplog.util import Timer

N_FEATURES = 2 ** 24
MIN_SAMPLES = 3  # Minimum number of messages to form a cluster
LOGGER = logging.getLogger(__name__)


def process(
        event_iterator: Iterator[str],
        max_samples_per_cluster: int,
        max_noisy_samples: int,
        max_distance: float,
) -> ClusteringAccumulator:
    events_original = []
    tokens_list = []

    analysis_timer = Timer()
    for event in event_iterator:
        event = event.strip()
        events_original.append(event)
        tokens_list.append(DEFAULT_ANALYZER.analyze(event))
    LOGGER.debug(f"Text analysis completed duration={analysis_timer.elapsed_ms()}ms")

    feature_hasher = FeatureHasher(input_type="string", n_features=N_FEATURES)
    sparse_matrix = feature_hasher.transform(tokens_list)

    clustering_timer = Timer()
    clustering = DBSCAN(min_samples=MIN_SAMPLES, eps=max_distance, metric="l1").fit(sparse_matrix)
    LOGGER.debug(f"Clustering completed duration={clustering_timer.elapsed_ms()}ms")
    accumulator = ClusteringAccumulator(max_samples_per_cluster, max_noisy_samples)
    for cluster_id, line_nr, event in zip(clustering.labels_, range(1, len(events_original) + 1), events_original):
        event2 = LogEvent(line_nr, event)
        if cluster_id >= 0:
            accumulator.report_event(int(cluster_id), event2)
        else:
            accumulator.report_noisy_event(event2)
    return accumulator
