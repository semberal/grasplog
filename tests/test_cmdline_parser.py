import unittest

from grasplog.datamodel import OutputFormat
from grasplog.exception import InvalidCmdLineArgException
from grasplog.cli import create_app_config


class CmdLineParserTestCase(unittest.TestCase):
    def test_happy_path_parsing(self):
        app_config = create_app_config(
            args=["--max-samples-per-cluster", "3", "--max-noisy-samples", "5", "--output-format", "json", "path1"]
        )
        self.assertEqual(OutputFormat.json_format, app_config.output_format)
        self.assertEqual("path1", app_config.path_glob)
        self.assertEqual(3, app_config.max_samples_per_cluster)
        self.assertEqual(5, app_config.max_noisy_samples)

    def test_custom_validation(self):
        with self.assertRaises(InvalidCmdLineArgException) as context:
            create_app_config(["--max-samples-per-cluster", "0", "path1"])
        self.assertEqual("MAX_SAMPLES_PER_CLUSTER argument must be an integer greater than 1", str(context.exception))

        with self.assertRaises(InvalidCmdLineArgException) as context:
            create_app_config(["--max-noisy-samples", "-1", "path1"])
        self.assertEqual("MAX_NOISY_SAMPLES argument must be an integer greater than 1", str(context.exception))

        with self.assertRaises(InvalidCmdLineArgException) as context:
            create_app_config(["--max-distance", "-1.1", "path1"])
        self.assertEqual(
            "MAX_DISTANCE argument must be greater than 0, floating point numbers are allowed (e.g. '2.1')",
            str(context.exception)
        )

    def test_noisy_count_taken_from_cluster_size(self):
        app_config = create_app_config(
            args=["--max-samples-per-cluster", "11", "path1"]
        )
        self.assertEqual(11, app_config.max_noisy_samples)
