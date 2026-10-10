from app.services.ingestion.identity import generate_document_id


def test_same_filename_generates_same_id():
    id_1 = generate_document_id(
        "employee_policy.pdf"
    )

    id_2 = generate_document_id(
        "employee_policy.pdf"
    )

    assert id_1 == id_2


def test_filename_case_is_normalized():
    id_1 = generate_document_id(
        "Employee_Policy.PDF"
    )

    id_2 = generate_document_id(
        "employee_policy.pdf"
    )

    assert id_1 == id_2


def test_different_filename_generates_different_id():
    id_1 = generate_document_id(
        "employee_policy.pdf"
    )

    id_2 = generate_document_id(
        "leave_policy.pdf"
    )

    assert id_1 != id_2


def test_document_id_length():
    document_id = generate_document_id(
        "employee_policy.pdf"
    )

    assert len(document_id) == 16