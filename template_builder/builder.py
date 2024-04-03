import abc
from typing import Type

import docxtpl
import loguru

from template_builder.dataset_collector import DatasetCollector
from template_builder.document_connector import DocumentConnector
from template_builder.synthax_validator import SynthaxValidator


class AbstractTemplateBuilderFactory(abc.ABC):

    def __init__(self):
        raise NotImplementedError("Cannot initialize abstract factory")

    @abc.abstractmethod
    def generate_template(self, *args, **kwargs) -> docxtpl.DocxTemplate:
        pass

    @abc.abstractmethod
    def create_dataset_collector(self) -> DatasetCollector:
        pass

    @abc.abstractmethod
    def create_document_connector(self) -> Type[DocumentConnector]:
        pass

    @abc.abstractmethod
    def create_synthax_validator(self, template, data) -> SynthaxValidator:
        pass


class TemplateBuilderFactory(AbstractTemplateBuilderFactory):
    def __init__(self, dataset: dict, ordered_templates: dict):
        self._initial_dataset = dataset
        self._ordered_templates = ordered_templates

    def generate_template(self, *args, **kwargs) -> docxtpl.DocxTemplate:
        collector = self.create_dataset_collector()
        connector = self.create_document_connector()
        templates, data = collector.collect()

        for template, single_data in zip(templates, data):
            loguru.logger.debug(f"Valitating {template=} with {single_data=}")
            validator = self.create_synthax_validator(template, single_data)
            try:
                validator.validate_synthax()
            except ValueError as e:
                loguru.logger.info(e)
        connected_doc = connector.connect_document_parts(self._initial_dataset)
        # connected_doc.render(DATASET)
        return connected_doc

    def create_dataset_collector(self) -> DatasetCollector:
        loguru.logger.debug(
            f"Creating DatasetCollector for {self._initial_dataset=}"
        )
        if not self._initial_dataset:
            raise ValueError(f"Got empty dataset for {self=}")
        return DatasetCollector(self._initial_dataset)

    def create_document_connector(self) -> DocumentConnector:
        loguru.logger.debug(
            f"Creating DocumentConnector for {self._initial_dataset=}"
        )
        if not self._ordered_templates:
            raise ValueError(f"Got no templates for {self=}")
        return DocumentConnector(self._ordered_templates)

    def create_synthax_validator(self, template, data) -> SynthaxValidator:
        return SynthaxValidator(template, data)

    @property
    def template_paths(self):
        return [*self._ordered_templates.keys()]

    @property
    def template_ordering(self):
        return [*self._ordered_templates.values()]
