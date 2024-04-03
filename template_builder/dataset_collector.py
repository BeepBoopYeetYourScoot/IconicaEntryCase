import pathlib
from typing import Tuple, List

import loguru
from docxtpl import DocxTemplate


class DatasetCollector:

    def __init__(self, initial_dataset: dict):
        """
        Document collector interface
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
