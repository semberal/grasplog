import unittest

from grasplog.ml import text_processing


class TextAnalyzersTestCase(unittest.TestCase):
    def test_simple_tokenizer(self):
        t = text_processing.SimpleTokenizer()
        self.assertEqual(["foo_bar", "-", "baz"], t.tokenize("foo_bar-baz"))

    def test_lower_casing_filter(self):
        t = text_processing.LowerCasingFilter()
        self.assertEqual("foo bar tři", t.filter("Foo BAR TŘI"))

    def test_numeric_token_filter(self):
        t = text_processing.NumericTokenFilter()
        self.assertEqual(["a11", ""], t.filter(["123", "1", "a11", "011", ""]))

    def test_single_char_token_filter(self):
        t = text_processing.SingleCharTokenFilter()
        self.assertEqual(["a", "ab", "*/", "č"], t.filter(["a", "/", "1", ".", "", "ab", "*/", "č"]))

    def test_ngram_tokenizer(self):
        separator = "##___##"
        base_tokens = ["foo_bar", "-", "baz"]
        self.assertEqual(
            ["foo_bar", "-", "baz", f"foo_bar{separator}-", f"-{separator}baz"],
            text_processing.NgramTokenStreamEnricher([2]).filter(base_tokens),
        )
        self.assertEqual(
            [
                "foo_bar", "-", "baz",
                f"foo_bar{separator}-", f"-{separator}baz",
                f"foo_bar{separator}-{separator}baz"
            ],
            text_processing.NgramTokenStreamEnricher([2, 3]).filter(base_tokens),
        )
