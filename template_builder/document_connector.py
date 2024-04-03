import pathlib
from typing import Dict, Union

import loguru
from docxtpl import DocxTemplate


class DocumentConnector:

    def __init__(
        self,
        ordered_templates: Dict[pathlib.Path, int],
    ):
        """
        Interface for connecting documents
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
