from docxtpl import DocxTemplate

HEADING_1_VARS = {
    "addition_text": "Приложение 11 \n к Регламенту подготовки и контроля "
    "выполнения мероприятий плана работы",
    "company_var": "{company_name}",
    "project_text": "Проект",
    "project_var": "{specified_project}",
}
HEADING_2_VARS = {
    "heading_2_text": "Приложение №",
    "number_var": "{number_var}",
    "heading_2_continued": "к Порядку реализации активов ликвидируемых "
    "финансовых организаций",
}
BODY_1_VARS = {
    "block_1": "Государственная корпорация ",
    "company_var": "'{company_name}'",
    "company_address": "{specified_address}",
    "block_2": ", являющаяся на основании решения Арбитражного суда",
    "court_name": "{official_court}",
}
BODY_2_VARS = {"tablerowa": ["a", "b", "c"]}
BOTTOM_1_VARS = {}
BOTTOM_2_VARS = {}

TEMPLATE_FILENAME = "subdocs_fixtures/heading_1.docx"
RESULT_FILENAME = "result.docx"

if __name__ == "__main__":
    test_doc = DocxTemplate(TEMPLATE_FILENAME)
    test_doc.render(HEADING_1_VARS)
    test_doc.save(RESULT_FILENAME)
