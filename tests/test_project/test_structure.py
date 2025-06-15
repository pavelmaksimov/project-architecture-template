import pytest


@pytest.mark.skip  # TODO: remove
def test_module_names(modules_map):
    """Merchants check in module names."""
    assert "model" not in modules_map, "Must be models.py"
    assert "services" not in modules_map, "Must be services.py"
    assert "repo" not in modules_map, "Must be repository.py"
    assert "repos" not in modules_map, "Must be repository.py"
    assert "repositories" not in modules_map, "Must be repository.py"
    assert "dao" not in modules_map, "use repository.py"
    assert "interface" not in modules_map, "Must be interfaces.py"
    assert "schema" not in modules_map, "Must be schemas.py"
    assert "enum" not in modules_map, "Must be enums.py"
    assert "validations" not in modules_map, "Must be validation.py"
    assert "use_case" not in modules_map, "Must be use_cases.py"
    assert "endpoint" not in modules_map, "Must be endpoints.py"
    assert "exception" not in modules_map, "Must be exceptions.py"
    assert "handler" not in modules_map, "Must be handlers.py"
    assert "test" not in modules_map, "It should be in the directory of tests"
    assert "tests" not in modules_map, "It should be in the directory of tests"

    for module in modules_map:
        assert module.islower(), "Must be lowercase"
        assert module.startswith("test_") or module.startswith("tests_"), "It should be in the directory of tests"
