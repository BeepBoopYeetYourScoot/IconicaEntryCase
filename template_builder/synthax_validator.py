import loguru
from docxtpl import DocxTemplate
from jinja2 import TemplateSyntaxError


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
