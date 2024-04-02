import abc
import os
import pathlib
from typing import Type, List, Iterable, Dict, Tuple

import docxtpl
import loguru
from docxtpl import DocxTemplate
from jinja2 import TemplateSyntaxError


class DatasetCollector:

    def __init__(self, template_path: pathlib.Path, dataset_vars: dict):
        if not isinstance(dataset_vars, dict):
            raise ValueError(
                f"Expected {dict=}, got {type(dataset_vars)=} instead"
            )
        self._template = DocxTemplate(template_path)
        self._dataset_vars = dataset_vars
        self._documents = []

    def collect(self) -> List[DocxTemplate]:
        loguru.logger.debug(f"Collecting templates for {self=}")
        self._documents = [
            DocxTemplate(file_path) for file_path, count in self._dataset_vars
        ]
        loguru.logger.debug(
            f"Got {len(self._documents)=} and " f"{len(self._dataset_vars)=}"
        )
        return self._documents

    @property
    def template(self):
        return self._template

    @property
    def original_file_paths(self) -> List[pathlib.Path]:
        return list(self._dataset_vars.keys())

    @property
    def ordering(self) -> List[int]:
        return list(self._dataset_vars.values())

    @property
    def documents(self):
        return self._documents


class DocumentConnector:

    def __init__(
        self,
        ordered_templates: Dict[pathlib.Path, int],
    ):
        self._ordered_templates = ordered_templates

    @property
    def connect_document_parts(self):
        loguru.logger.debug(
            f"Connecting documents: \n {self._ordered_templates=}"
        )
        templates = self._get_sorted_templates()
        header_num, header_path = templates.pop()
        header_template = DocxTemplate(header_path)

        for num, doc_path in templates:
            header_template.new_subdoc(doc_path)
        return self.header_template

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
    def create_dataset_collector(self, template_path) -> DatasetCollector:
        pass

    @abc.abstractmethod
    def create_document_generator(self) -> Type[DocumentConnector]:
        pass

    @abc.abstractmethod
    def create_synthax_validator(self) -> SynthaxValidator:
        pass


class TemplateBuilderFactory(AbstractTemplateBuilderFactory):
    def __init__(self, dataset: dict, ordered_templates: dict):
        self._initial_dataset = dataset
        self._ordered_templates = ordered_templates
        self._template_collection = []

    def create_dataset_collector(self, template_path) -> DatasetCollector:
        loguru.logger.debug(
            f"Creting DatasetCollector for {self._initial_dataset=}"
        )
        if not self._initial_dataset:
            raise ValueError(f"Got empty dataset for {self=}")
        return DatasetCollector(template_path, self._initial_dataset)

    def create_document_generator(self) -> DocumentConnector:
        loguru.logger.debug(
            f"Creating DocumentConnector for {self._initial_dataset=}"
        )
        if not self._ordered_templates:
            raise ValueError(f"Got no templates for {self=}")
        return DocumentConnector(self._ordered_templates)

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


if __name__ == "__main__":
    pass
