import pytest

from ipe.targets.python.naming import PythonNaming


@pytest.fixture
def naming() -> PythonNaming:
    return PythonNaming()


class TestPythonNamingClassName:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("Pet", "Pet"),
            ("pet_store", "PetStore"),
            ("HTTPResponse", "HttpResponse"),
            ("user", "User"),
        ],
    )
    def test_conversions(self, naming: PythonNaming, raw: str, expected: str):
        assert naming.class_name(raw) == expected


class TestPythonNamingMethodName:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("listPets", "list_pets"),
            ("createPet", "create_pet"),
            ("showPetById", "show_pet_by_id"),
            ("already_snake", "already_snake"),
        ],
    )
    def test_conversions(self, naming: PythonNaming, raw: str, expected: str):
        assert naming.method_name(raw) == expected

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("class", "class_"),
            ("type", "type_"),
            ("return", "return_"),
            ("import", "import_"),
            ("match", "match_"),
        ],
    )
    def test_keyword_safety(self, naming: PythonNaming, raw: str, expected: str):
        assert naming.method_name(raw) == expected


class TestPythonNamingFieldName:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("petId", "pet_id"),
            ("user_name", "user_name"),
            ("type", "type_"),
            ("from", "from_"),
        ],
    )
    def test_conversions(self, naming: PythonNaming, raw: str, expected: str):
        assert naming.field_name(raw) == expected


class TestPythonNamingModuleName:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("PetStore", "pet_store"),
            ("user-service", "user_service"),
            ("import", "import_"),
        ],
    )
    def test_conversions(self, naming: PythonNaming, raw: str, expected: str):
        assert naming.module_name(raw) == expected
