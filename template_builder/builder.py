import abc
import os
import pathlib
from typing import Type, List, Iterable, Dict, Tuple

import docxtpl
import loguru
from docxtpl import DocxTemplate
from jinja2 import TemplateSyntaxError

from template_builder.fixtures import (
    HEADING_1_VARS,
    HEADING_2_VARS,
    BODY_1_VARS,
)


class DatasetCollector:

    def __init__(self, initial_dataset: dict):
        """
        Uses keys in initial dataset to create template collection
        :param initial_dataset:
        """
        if not isinstance(initial_dataset, dict):
            raise ValueError(
                f"Expected {dict=}, got {type(initial_dataset)=} instead"
            )
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
        self._ordered_templates = ordered_templates

    def connect_document_parts(self) -> DocxTemplate:
        loguru.logger.debug(
            f"Connecting documents: \n {self._ordered_templates=}"
        )
        templates = self._get_sorted_templates()
        header_num, header_path = templates.pop()
        header_template = DocxTemplate(header_path)

        for num, doc_path in templates:
            header_template.new_subdoc(doc_path)
        return header_template

    @property
    def template_paths(self):
        return [*self._ordered_templates.keys()]

    def _get_sorted_templates(self):
        turned = {v: k for k, v in self._ordered_templates}
        zipped = [*zip(turned.items())]
        zipped.sort(key=lambda x: x[0])
        return zipped


class SynthaxValidator:

    def __init__(self, template: DocxTemplate, template_data: dict):
        self._template = template
        self._template_data = template_data

    def validate_synthax(self):
        loguru.logger.debug(f"Validating syntax for {self._template=}")
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
        self._template_collection = []

    def generate_template(self, *args, **kwargs) -> docxtpl.DocxTemplate:
        collector = self.create_dataset_collector()
        connector = self.create_document_connector()
        templates, data = collector.collect()

        for template, single_data in zip(templates, data):
            loguru.logger.debug(f"Valitating {template=} with {single_data=}")
            validator = self.create_synthax_validator(template, single_data)
            validator.validate_synthax()
        return connector.connect_document_parts()

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

    def form_templates(self):
        loguru.logger.debug(f"Assigning template for {self=}")
        if not self._ordered_templates:
            raise ValueError(f"Got no templates for {self=}")
        for template_path, ordering in self._ordered_templates.items():
            assert isinstance(template_path, pathlib.Path)
            assert template_path.is_file()
            template = DocxTemplate(template_path)
            self._template_collection.append(template)
        return self._template_collection

    @property
    def template_collection(self):
        return self._template_collection

    @property
    def template_paths(self):
        return [*self._ordered_templates.keys()]

    @property
    def template_ordering(self):
        return [*self._ordered_templates.values()]


FIXTURE_FOLDER = pathlib.Path("subdocs_fixtures")
DATASET = {
    "subdocs_fixtures/header_1.docx": HEADING_1_VARS,
    "subdocs_fixtures/header_2.docx": HEADING_2_VARS,
    "subdocs_fixtures/body_1.docx": BODY_1_VARS,
}
ORDERED_TEMPLATES = {
    "subdocs_fixtures/header_1.docx": 0,
    "subdocs_fixtures/header_2.docx": 1,
    "subdocs_fixtures/body_1.docx": 2,
}

DATASETS = [(DATASET, ORDERED_TEMPLATES), (None, None)]


def main():
    for dataset, templates in DATASETS:
        factory = TemplateBuilderFactory(dataset, templates)
        factory.generate_template()


if __name__ == "__main__":
    main()
