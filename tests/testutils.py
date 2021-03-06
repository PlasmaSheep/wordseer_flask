"""
Unit tests for the utils module.
"""

import unittest
import pdb

import mock

from app import app
from app import db
from app.uploader.models import Sequence
from app.uploader.models import Word
from app.wordseer import utils
from app.wordseer.models import SequenceSet
import common

class TestUtils(unittest.TestCase):
    """Test the utils module.
    """
    @classmethod
    def setUpClass(cls):
        common.reset_db()
        cls.word1 = Word(word="foo", lemma="bar")
        cls.word2 = Word(word="foo", lemma="baz")
        cls.word3 = Word(word="bar", lemma="bar")
        cls.word4 = Word(word="baz", lemma="qux")

        sequence1 = Sequence(words=[cls.word1, cls.word2])
        sequence2 = Sequence(words=[cls.word4])
        sequence3 = Sequence(words=[cls.word3])
        cls.sequenceset1 = SequenceSet(sequences=[sequence1, sequence2])
        cls.sequenceset2 = SequenceSet(sequences=[sequence3])

        db.session.add_all([sequence1, sequence2, sequence3, cls.sequenceset1,
            cls.sequenceset2, cls.word1, cls.word2, cls.word3, cls.word4])
        db.session.commit()

    def test_table_exists(self):
        """Test to make sure that table_exists recognizes every existing table
        and not tables that don't exist.
        """

        for table_name in db.metadata.tables.keys():
            self.failUnless(utils.table_exists(table_name))

        self.failIf(utils.table_exists("foobarbazfoo"))

    def test_remove_spaces_around_punctuation(self):
        """Test to make sure that spaces are removed properly in
        remove_spaces_around_punctuation.
        """

        before_set = set(app.config["PUNCTUATION_NO_SPACE_BEFORE"])
        after_set = set(app.config["PUNCTUATION_NO_SPACE_AFTER"])

        only_before = before_set - after_set
        only_after = after_set - before_set
        both = before_set & after_set

        sentence = (
            u" x " +
            u" x ".join(only_after) +
            u" x " +
            u" x ".join(only_before) +
            u" x " +
            u" x ".join(both)
        )
        expected = (
            u" x " +
            u"x ".join(only_after) +
            u"x" +
            u" x".join(only_before) +
            u" x" +
            u"x".join(both)
        )

        assert expected == utils.remove_spaces_around_punctuation(sentence)

    def test_get_lemma_variant_ids(self):
        """Test get_lemma_variant_ids().
        """

        variant_ids = utils.get_lemma_variant_ids("foo")

        assert sorted(variant_ids) == sorted([self.word1.id, self.word2.id,
            self.word3.id])

    def test_get_lemma_variants(self):
        """Test get_lemma_variants()
        """

        variants = utils.get_lemma_variants("foo")

        assert sorted(variants) == sorted([self.word1.word, self.word2.word,
            self.word3.word])

    @mock.patch("app.wordseer.utils.request", autospec=True)
    def test_get_word_ids_from_sequence_set(self, mock_request):
        """Test the get_word_ids_from_sequence_set method with
        all_word_forms on.
        """

        mock_request.args = {"all_word_forms": "off"}

        with app.test_request_context():
            word_ids = utils.get_word_ids_from_sequence_set(
                self.sequenceset1.id)

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id,
            self.word4.id])


    @mock.patch("app.wordseer.utils.request", autospec=True)
    def test_lemmatize_get_word_ids_from_sequence_set(self, mock_request):
        """Test the get_word_ids_from_sequence_set method with
        all_word_forms off.
        """

        mock_request.args = {"all_word_forms": "on"}

        with app.test_request_context():
            word_ids = utils.get_word_ids_from_sequence_set(
                self.sequenceset1.id)

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id,
            self.word3.id, self.word4.id])

    @mock.patch("app.wordseer.utils.request", autospec=True)
    def test_get_word_ids_from_surface_word(self, mock_request):
        """Test the get_word_ids_from_surface_word method with all_word_forms
        off.
        """

        mock_request.args = {"all_word_forms": "off"}

        with app.test_request_context():
            word_ids = utils.get_word_ids_from_surface_word("fo*")

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id])

    @unittest.skip("Waiting for clarification")
    @mock.patch("app.wordseer.utils.request", autospec=True)
    def test_get_word_ids_from_surface_word(self, mock_request):
        """Test the get_word_ids_from_surface_word method with all_word_forms
        on.
        """

        mock_request.args = {"all_word_forms": "on"}

        with app.test_request_context():
            word_ids = utils.get_word_ids_from_surface_word("fo*")

        pdb.set_trace()

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id])

