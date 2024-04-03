import abc
import pathlib
from typing import Type, List, Dict, Tuple, Union

import docxtpl
import loguru
from docxtpl import DocxTemplate
from jinja2 import TemplateSyntaxError

from template_builder.fixtures import (
    DATASETS,
    RESULT_FILENAME,
)


class DatasetCollector:

    def __init__(self, initial_dataset: dict):
        """
        Uses keys in initial dataset to create template collection
        """
        if not isinstance(initial_dataset, dict):
            raise ValueError(
                f"Expected {dict=}, got {type(initial_dataset)=} instead"
            )
        assert len(initial_dataset) > 0
        self._initial_dataset = initial_dataset
        self._documents = []
        self._data = [*initial_dataset.values()]

    def collect(self) -> Tuple[List[DocxTemplate], List[dict]]:
        loguru.logger.debug(f"Collecting templates for {self=}")
        self._documents = [
            DocxTemplate(file_path)
            for file_path in self._initial_dataset.keys()
        ]
        loguru.logger.debug(
            f"Got {len(self._documents)=} and "
            f"{len(self._initial_dataset)=}"
        )
        loguru.logger.debug(f"Returning with {self._data=}")
        return self._documents, self._data

    @property
    def dataset(self):
        return self._initial_dataset

    @property
    def original_file_paths(self) -> List[pathlib.Path]:
        return list(self._initial_dataset.keys())

    @property
    def ordering(self) -> List[int]:
        return list(self._initial_dataset.values())

    @property
    def documents(self):
        return self._documents


class DocumentConnector:

    def __init__(
        self,
        ordered_templates: Dict[pathlib.Path, int],
    ):
        """
        Connects together multiple templates
        """
        self._ordered_templates = ordered_templates
        self._template_collection = []

    def connect_document_parts(
        self, dataset: Dict[Union[pathlib.Path, str], dict]
    ) -> DocxTemplate:
        loguru.logger.debug(
            f"Connecting documents: \n {self._ordered_templates=}"
        )
        ordered_dataset = self.connect_dataset_and_ordering(dataset)
        header_info = ordered_dataset.pop()
        loguru.logger.debug(f"{header_info=}")
        header_template = DocxTemplate(header_info[0])

        for template_data in ordered_dataset:
            header_template.new_subdoc(template_data[0])
        return header_template

    def connect_dataset_and_ordering(self, dataset):
        ordered = self._ordered_templates.copy()
        connected = []
        for tmpl, data in dataset.items():
            num = ordered.pop(tmpl)
            connected.append((tmpl, data, num))
        connected.sort(key=lambda x: x[2])
        return connected


class SynthaxValidator:

    def __init__(self, template: DocxTemplate, template_data: dict):
        self._template = template
        self._template_data = template_data
        loguru.logger.debug(f"{self._template=}")
        loguru.logger.debug(f"{self._template_data=}")

    def validate_synthax(self):
        assert isinstance(self._template, DocxTemplate)
        try:
            self._render_template()
        except TemplateSyntaxError as e:
            loguru.logger.error(
                f"Got error while validating " f"{self._template=}"
            )
            raise ValueError(e)

    def _render_template(self):
        self._template.render(self._template_data)


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


def main():
    for dataset, templates in DATASETS:
        factory = TemplateBuilderFactory(dataset, templates)
        result = factory.generate_template()
        result.save(RESULT_FILENAME)


if __name__ == "__main__":
    main()
