import unittest
from grasplog.ml.clustering import process


class ClusteringTestCase(unittest.TestCase):
    def test_simple_clustering(self):
        lines = [
            "Error foo bar",
            "INFO all good",
            "Error foo bar",
            "Error foo bar",
            "INFO all good",
            "INFO all good",
            "DEBUG something else",
            "Error foo bar",
        ]

        accumulator = process(lines, 3, 3, 1)
        self.assertEqual(2, len(accumulator.clusters))

        errors_cluster_id = 0 if "Error" in accumulator.clusters[0].samples[0].message else 1
        infos_cluster_id = 0 if errors_cluster_id == 1 else 1

        self.assertEqual(["Error foo bar"] * 3, [x.message for x in accumulator.clusters[errors_cluster_id].samples])
        self.assertEqual([1, 3, 4], [x.line_nr for x in accumulator.clusters[errors_cluster_id].samples])
        self.assertEqual(4, accumulator.clusters[errors_cluster_id].total_event_count)
        self.assertEqual(0, accumulator.clusters[errors_cluster_id].cluster_id)

        self.assertEqual(["INFO all good"] * 3, [x.message for x in accumulator.clusters[infos_cluster_id].samples])
        self.assertEqual([2, 5, 6], [x.line_nr for x in accumulator.clusters[infos_cluster_id].samples])
        self.assertEqual(3, accumulator.clusters[infos_cluster_id].total_event_count)
        self.assertEqual(1, accumulator.clusters[infos_cluster_id].cluster_id)

        self.assertEqual(["DEBUG something else"], [x.message for x in accumulator.noisy_events.samples])
        self.assertEqual([7], [x.line_nr for x in accumulator.noisy_events.samples])
        self.assertEqual(1, accumulator.noisy_events.total_event_count)
