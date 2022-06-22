import unittest

from grasplog.json_output import ClusterInfoJson, ClusteringJson, serialize, LogEventJson, NoisyEventsJson


class TestJsonSerialization(unittest.TestCase):
    def test_json_output(self):
        cluster1 = ClusterInfoJson(1, [LogEventJson(1, "foo"), LogEventJson(2, "bar")], 2)
        cluster2 = ClusterInfoJson(2, [LogEventJson(3, "baz")], 1)
        clustering_json = ClusteringJson(
            [cluster1, cluster2],
            NoisyEventsJson([LogEventJson(4, "abc"), LogEventJson(5, "def")], 2)
        )
        clustering_json_str = serialize(clustering_json)
        self.assertEqual(clustering_json_str,
                         """{
  "clusters": [
    {
      "id": 1,
      "samples": [
        {
          "lineNumber": 1,
          "event": "foo"
        },
        {
          "lineNumber": 2,
          "event": "bar"
        }
      ],
      "totalCount": 2
    },
    {
      "id": 2,
      "samples": [
        {
          "lineNumber": 3,
          "event": "baz"
        }
      ],
      "totalCount": 1
    }
  ],
  "noisySamples": {
    "samples": [
      {
        "lineNumber": 4,
        "event": "abc"
      },
      {
        "lineNumber": 5,
        "event": "def"
      }
    ],
    "totalCount": 2
  }
}""")

    def test_empty_json_output(self):
        self.assertEqual(serialize(ClusteringJson([], NoisyEventsJson([], 0))),
                         """{
  "clusters": [],
  "noisySamples": {
    "samples": [],
    "totalCount": 0
  }
}""")
