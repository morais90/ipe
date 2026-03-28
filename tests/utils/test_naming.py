import pytest

from ipe.utils.naming import to_pascal_case, to_snake_case


class TestToSnakeCase:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("PetStore", "pet_store"),
            ("petStore", "pet_store"),
            ("pet_store", "pet_store"),
            ("pet-store", "pet_store"),
            ("pet store", "pet_store"),
            ("pet.store", "pet_store"),
            ("HTTPResponse", "http_response"),
            ("getHTTPResponse", "get_http_response"),
            ("XMLParser", "xml_parser"),
            ("simpleXML", "simple_xml"),
            ("OAuth2Token", "o_auth2_token"),
            ("userID", "user_id"),
            ("listPets", "list_pets"),
            ("createPet", "create_pet"),
            ("showPetById", "show_pet_by_id"),
            ("already_snake", "already_snake"),
            ("ALL_CAPS", "all_caps"),
            ("a", "a"),
            ("A", "a"),
            ("", ""),
        ],
    )
    def test_conversions(self, raw: str, expected: str):
        assert to_snake_case(raw) == expected


class TestToPascalCase:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("pet_store", "PetStore"),
            ("pet-store", "PetStore"),
            ("pet store", "PetStore"),
            ("pet.store", "PetStore"),
            ("petStore", "PetStore"),
            ("PetStore", "PetStore"),
            ("HTTPResponse", "HttpResponse"),
            ("http_response", "HttpResponse"),
            ("list_pets", "ListPets"),
            ("user_id", "UserId"),
            ("a", "A"),
            ("", ""),
        ],
    )
    def test_conversions(self, raw: str, expected: str):
        assert to_pascal_case(raw) == expected
