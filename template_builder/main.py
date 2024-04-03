from template_builder.builder import TemplateBuilderFactory
from template_builder.fixtures import DATASETS, RESULT_FILENAME


def main():
    for dataset, templates in DATASETS:
        factory = TemplateBuilderFactory(dataset, templates)
        result = factory.generate_template()
        result.save(RESULT_FILENAME)


if __name__ == "__main__":
    main()
