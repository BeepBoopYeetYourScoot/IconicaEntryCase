import pytest

from template_builder.builder import (
    TemplateBuilderFactory,
    DatasetCollector,
    DocumentConnector,
    SynthaxValidator,
)
from template_builder.fixtures import DATASET, ORDERED_TEMPLATES


class TestBuilderFactory:
    factory = TemplateBuilderFactory(DATASET, ORDERED_TEMPLATES)

    def test_create_dataset_collector(self):
        res = self.factory.create_dataset_collector()
        assert isinstance(res, DatasetCollector)

    def test_create_document_connector(self):
        res = self.factory.create_document_connector()
        assert isinstance(res, DocumentConnector)

    def test_create_synthax_validator(self):
        res = self.factory.create_synthax_validator()
        assert isinstance(res, SynthaxValidator)


class TestDatasetCollector:
    single_data_collector = DatasetCollector(DATASET.pop())
    multiple_data_collector = DatasetCollector(DATASET)

    def test_zero_collector(self):
        try:
            DatasetCollector({})
        except AssertionError:
            assert True
        assert False

    def test_single_collector_initial(self):
        res = self.single_data_collector.collect()
        assert isinstance(res, tuple)
        docs, data = res[0], res[1]
        assert isinstance(docs, list)
        assert isinstance(data, list)

    def test_multiple_collector_initial(self):
        res = self.multiple_data_collector.collect()
        assert isinstance(res, tuple)
        docs, data = res[0], res[1]
        assert isinstance(docs, list)
        assert isinstance(data, list)

    def test_single_collector_indepth(self):
        res = self.single_data_collector.collect()
        docs, data = res[0], res[1]
        assert len(docs) == 1

    def test_multiple_collector_indepth(self):
        res = self.multiple_data_collector.collect()
        docs, data = res[0], res[1]
        assert len(docs) == len(DATASET)
