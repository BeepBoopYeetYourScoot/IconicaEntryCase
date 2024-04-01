from docxtpl import DocxTemplate

HEADING_1_VARS = {
    "addition_text": "Приложение 11 \n к Регламенту подготовки и контроля "
    "выполнения мероприятий плана работы",
    "company_var": "{company_name}",
    "project_text": "Проект",
    "project_var": "{project_var}",
}
HEADING_2_VARS = {
    "heading_2_text": "Приложение №",
    "number_var": "{number_var}",
    "heading_2_continued": "к Порядку реализации активов ликвидируемых "
    "финансовых организаций",
}
BODY_1_VARS = {}
BODY_2_VARS = {"tablerowa": ["a", "b", "c"]}
BOTTOM_1_VARS = {}
BOTTOM_2_VARS = {}

TEMPLATE_FILENAME = "subdocs_fixtures/base.docx"
RESULT_FILENAME = "result.docx"

if __name__ == "__main__":
    test_doc = DocxTemplate(TEMPLATE_FILENAME)
    test_doc.render(BODY_2_VARS)
    test_doc.save(RESULT_FILENAME)
