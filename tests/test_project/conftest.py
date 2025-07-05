import pathlib
from collections import defaultdict
import pytest

PRESENTATION_MODULES = [
    "cli",
    "endpoints",
    "handlers",
]
INFRASTRUCTURE_MODULES = ["repository", "models", *PRESENTATION_MODULES]
BUSSINES_LOGIC_MODULES = [
    "use_cases",
    "service",
    "aggregates",
    "entities",
    "value_objects",
    "validation",
]
HELPER_MODULES = [
    "schemas",
    "enums",
    "interfaces",
    "exceptions",
]
INFRA_PATTERNS = ["project.infrastructure.*", "project.presentation.*"]


def iter_domain_modules(project_dir: pathlib.Path):
    """
    :return: {"domain": ["module", ...]}
    """
    domains_dir = project_dir / "domains"
    for domain_dir in domains_dir.iterdir():
        if domain_dir.is_dir() and not domain_dir.name.startswith("_"):
            for file in domain_dir.iterdir():
                if file.is_file() and file.suffix == ".py" and not file.name.startswith("_"):
                    module_name = file.stem
                    yield domain_dir.name, module_name, f"project.domains.{domain_dir.name}.{module_name}"


@pytest.fixture(scope="session")
def domains_map(project_dir):
    """
    :return: {"domain": ["module", ...]}
    """
    result = {}
    for domain, _, full_path in iter_domain_modules(project_dir):
        result.setdefault(domain, []).append(full_path)
    return result


@pytest.fixture(scope="session")
def modules_map(project_dir):
    """
    :return: {"module": ["domain", ...]}
    """
    result = defaultdict(list)
    for _, module, full_path in iter_domain_modules(project_dir):
        result[module].append(full_path)
    return result


def get_filtered_modules(project_dir: pathlib.Path, filter_set):
    return [full_path for _, module, full_path in iter_domain_modules(project_dir) if module in filter_set]


@pytest.fixture(scope="session")
def infra_modules(project_dir):
    """
    :return: {"module": ["domain", ...]}
    """
    return INFRA_PATTERNS[:] + get_filtered_modules(project_dir, INFRASTRUCTURE_MODULES)


@pytest.fixture(scope="session")
def helper_modules(project_dir):
    """
    :return: {"module": ["domain", ...]}
    """
    return get_filtered_modules(project_dir, HELPER_MODULES)


@pytest.fixture(scope="session")
def bussines_modules(project_dir):
    """
    :return: {"module": ["domain", ...]}
    """
    return get_filtered_modules(project_dir, BUSSINES_LOGIC_MODULES)


@pytest.fixture(scope="session")
def presentation_modules(project_dir):
    """
    :return: {"module": ["domain", ...]}
    """
    return get_filtered_modules(project_dir, PRESENTATION_MODULES)
