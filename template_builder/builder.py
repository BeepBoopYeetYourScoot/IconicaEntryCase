import abc
import os
import pathlib
from typing import Type, List, Iterable

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


class DocumentGenerator:

    def __init__(
        self,
        heading_template: DocxTemplate,
        *template_paths: Iterable[DocxTemplate],
    ):
        self._heading = heading_template
        self._template_paths: Iterable[pathlib.Path] = [*template_paths]

    def generate_document(self):
        for doc_path in self._template_paths:
            self._heading.new_subdoc(doc_path)
        return self._heading

    @property
    def heading(self):
        return self._heading

    @property
    def template_paths(self):
        return self._template_paths


class SynthaxValidator:

    def __init__(self, template: DocxTemplate, template_data):
        self._template = template
        self._template_data = template_data

    def validate_synthax(self):
        loguru.logger.debug(f"Validating syntax for {self._template=}")
        try:
            self._false_render_template()
        except TemplateSyntaxError as e:
            loguru.logger.error(
                f"Got error while validating " f"{self._template=}"
            )
            raise ValueError(e)

    def _false_render_template(self):
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
    def create_document_generator(self) -> DocumentGenerator:
        pass

    @abc.abstractmethod
    def create_synthax_validator(self) -> SynthaxValidator:
        pass


class BuilderFactory(AbstractTemplateBuilderFactory):
    def __init__(self, dataset: dict, ordered_templates: dict):
        self._initial_dataset = dataset
        self._ordered_templates = ordered_templates
        self._template_collection = []

    def create_dataset_collector(self, template_path) -> DatasetCollector:
        loguru.logger.debug(
            f"Creting DatasetCollector for " f"{self._initial_dataset=}"
        )
        return DatasetCollector(template_path, self._initial_dataset)

    def form_templates(self):
        loguru.logger.debug(f"Assigning template for {self=}")
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
