import os
from unittest import TestCase

os.environ["HLL_MAINTENANCE_CONTAINER"] = "1"
from rcon.arguments import max_arg_index, replace_params


class MaxArgsTest(TestCase):
    def test_string(self):
        assert max_arg_index("parameter") == 0

    def test_string_with_argument(self):
        assert max_arg_index("$1") == 1

    def test_string_with_multiple_arguments(self):
        assert max_arg_index("$2") == 2

    def test_list(self):
        assert max_arg_index(["parameter 1", "parameter 2"]) == 0

    def test_list_with_argument(self):
        assert max_arg_index(["$1", "$2"]) == 2

    def test_list_with_nested_argument(self):
        assert max_arg_index(["$1", ["$2", "$3"]]) == 3

    def test_dict(self):
        assert max_arg_index({"$3 ignored": "parameter1", "key": "parameter 2"}) == 0

    def test_dict_with_argument(self):
        assert max_arg_index({"$3 ignored": "$2", "key": "$1"}) == 2

    def test_dict_with_nested_argument(self):
        assert max_arg_index({"$4 ignored": "$2", "key": {"key2": "$3"}}) == 3


class ReplaceParamsTest(TestCase):
    ctx: dict[str, str] = {"player_name": "SOME_PLAYER_NAME"}
    args: list[str] = ["parameter1", "parameter2"]
    
    def test_string(self):
        assert replace_params(self.ctx, self.args, "parameter") == "parameter"

    def test_context_string(self):
        assert replace_params(self.ctx, [], "{player_name}") == "SOME_PLAYER_NAME"

    def test_string_with_argument(self):
        assert replace_params(self.ctx, self.args, "$1") == "parameter1"

    def test_string_with_multiple_arguments(self):
        assert replace_params(self.ctx, self.args, "$2") == "parameter2"

    def test_list(self):
        assert replace_params(self.ctx, self.args, ["parameter 1", "parameter 2"]) == ["parameter 1", "parameter 2"]

    def test_list_with_argument(self):
        assert replace_params(self.ctx, self.args, ["$1", "$2"]) == ["parameter1", "parameter2"]

    def test_list_with_nested_argument(self):
        assert replace_params(self.ctx, self.args, ["$1", ["$2", "$3"], ["{player_name}"]]) == ["parameter1", ["parameter2", "$3"], ["SOME_PLAYER_NAME"]]

    def test_dict(self):
        assert replace_params(self.ctx, self.args, {"$3 ignored": "parameter1", "key": "parameter 2"}) == {"$3 ignored": "parameter1", "key": "parameter 2"}

    def test_dict_with_argument(self):
        assert replace_params(self.ctx, self.args, {"$3 ignored": "$2", "key": "$1"}) == {"$3 ignored": "parameter2", "key": "parameter1"}

    def test_dict_with_nested_argument(self):
        assert replace_params(self.ctx, self.args, {"$4 ignored": "$2", "key": {"key2": "$3", "key3": "{player_name}"}}) == {"$4 ignored": "parameter2", "key": {"key2": "$3", "key3": "SOME_PLAYER_NAME"}}
