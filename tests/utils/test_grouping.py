from ipe.models.standard import StandardOperation
from ipe.utils.grouping import by_nested_path, by_path, by_tag


class TestByTag:
    def test_groups_by_first_tag(self):
        operations = [
            StandardOperation(
                operation_id="listPets", method="GET", path="/pets", tags=["pets"]
            ),
            StandardOperation(
                operation_id="createPet", method="POST", path="/pets", tags=["pets"]
            ),
            StandardOperation(
                operation_id="listUsers", method="GET", path="/users", tags=["users"]
            ),
        ]

        result = by_tag(operations)

        assert result == {
            "pets": [operations[0], operations[1]],
            "users": [operations[2]],
        }

    def test_falls_back_to_path_when_no_tag(self):
        operations = [
            StandardOperation(operation_id="listPets", method="GET", path="/pets"),
            StandardOperation(
                operation_id="getPet", method="GET", path="/pets/{petId}"
            ),
        ]

        result = by_tag(operations)

        assert result == {"pets": [operations[0], operations[1]]}

    def test_mixed_tagged_and_untagged(self):
        operations = [
            StandardOperation(
                operation_id="listPets", method="GET", path="/pets", tags=["animals"]
            ),
            StandardOperation(operation_id="health", method="GET", path="/health"),
        ]

        result = by_tag(operations)

        assert result == {
            "animals": [operations[0]],
            "health": [operations[1]],
        }

    def test_uses_first_tag_only(self):
        operations = [
            StandardOperation(
                operation_id="op",
                method="GET",
                path="/x",
                tags=["primary", "secondary"],
            ),
        ]

        result = by_tag(operations)

        assert result == {"primary": [operations[0]]}

    def test_tag_lowercased(self):
        operations = [
            StandardOperation(
                operation_id="op", method="GET", path="/x", tags=["Pets"]
            ),
        ]

        result = by_tag(operations)

        assert result == {"pets": [operations[0]]}

    def test_empty_operations(self):
        assert by_tag([]) == {}


class TestByPath:
    def test_groups_by_first_segment(self):
        operations = [
            StandardOperation(operation_id="listPets", method="GET", path="/pets"),
            StandardOperation(
                operation_id="getPet", method="GET", path="/pets/{petId}"
            ),
            StandardOperation(operation_id="listUsers", method="GET", path="/users"),
        ]

        result = by_path(operations)

        assert result == {
            "pets": [operations[0], operations[1]],
            "users": [operations[2]],
        }

    def test_skips_path_parameters(self):
        operations = [
            StandardOperation(
                operation_id="op", method="GET", path="/{tenantId}/items"
            ),
        ]

        result = by_path(operations)

        assert result == {"items": [operations[0]]}

    def test_root_path_goes_to_default(self):
        operations = [
            StandardOperation(operation_id="op", method="GET", path="/"),
        ]

        result = by_path(operations)

        assert result == {"root": [operations[0]]}

    def test_empty_operations(self):
        assert by_path([]) == {}


class TestByNestedPath:
    def test_nested_resources(self):
        operations = [
            StandardOperation(
                operation_id="listPosts", method="GET", path="/users/{userId}/posts"
            ),
            StandardOperation(
                operation_id="getPost",
                method="GET",
                path="/users/{userId}/posts/{postId}",
            ),
            StandardOperation(
                operation_id="listComments",
                method="GET",
                path="/users/{userId}/posts/{postId}/comments",
            ),
        ]

        result = by_nested_path(operations)

        assert result == {
            "users.posts": [operations[0], operations[1]],
            "users.posts.comments": [operations[2]],
        }

    def test_flat_paths(self):
        operations = [
            StandardOperation(operation_id="listPets", method="GET", path="/pets"),
            StandardOperation(
                operation_id="getPet", method="GET", path="/pets/{petId}"
            ),
        ]

        result = by_nested_path(operations)

        assert result == {"pets": [operations[0], operations[1]]}

    def test_skips_all_parameters(self):
        operations = [
            StandardOperation(
                operation_id="op", method="GET", path="/{tenantId}/users/{userId}/posts"
            ),
        ]

        result = by_nested_path(operations)

        assert result == {"users.posts": [operations[0]]}

    def test_root_path_goes_to_default(self):
        operations = [
            StandardOperation(operation_id="op", method="GET", path="/"),
        ]

        result = by_nested_path(operations)

        assert result == {"root": [operations[0]]}

    def test_empty_operations(self):
        assert by_nested_path([]) == {}
