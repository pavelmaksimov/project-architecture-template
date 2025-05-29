import pytest
import pytest_archon

"""
.match - модули для которых это правило должно соотвествовать.
.exclude - исключает модули, в которых будет проверка, добавлять после .match
.should_not_import - что запрешает импортировать
.should_import - только разрешает импортировать указанные модули
.may_import - исключение модулей соответствующих паттерну, заданному в .match
.check - в каком модуле проверяем

.check(..., skip_type_checking=True) - Убрать проверку импортов в секции проверки типов:
 
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        ...
    
"""


def test_domain_layer(infra_modules, presentation_modules, bussines_modules):
    """
    Business logic layer should not depend infrastructure and presentation layer.
    """
    (
        pytest_archon.archrule(
            "DomainLayerRules", comment="Business logic layer should not depend infrastructure and presentation layer"
        )
        .match(*bussines_modules)
        .should_not_import(*infra_modules, *presentation_modules)
        .check("project.domains", skip_type_checking=True)
    )


def test_presentation_layer(presentation_modules, infra_modules, bussines_modules):
    """
    The presentation layer should use business logic only through DIContainer.
    """
    (
        pytest_archon.archrule(
            "PresentationLayerRules",
            comment="The presentation layer should use business logic only through DIContainer.",
        )
        .match(*presentation_modules)
        .should_not_import(*bussines_modules, *infra_modules, *presentation_modules)
        .check("project.domains", skip_type_checking=True)
    )


def test_infrastructure_layer(infra_modules, bussines_modules):
    """
    Infrastructure layer should not depend on business logic.
    """
    (
        pytest_archon.archrule(
            "InfrastructureLayerRules", comment="Infrastructure layer should not depend on business logic"
        )
        .match(*infra_modules)
        .should_not_import(*bussines_modules)
        .check("project.infrastructure", skip_type_checking=True)
    )


def test_import_for_service(modules_map):
    """Service layer deeper Use Cases."""
    (
        pytest_archon.archrule("RuleForService", comment="Service layer should not depend on use cases")
        .match(*modules_map["service"])
        .should_not_import(*modules_map["use_cases"])
        .check("project.domains", skip_type_checking=True)
    )


def test_import_for_models(modules_map):
    """
    Data models should not depend on other modules.
    """
    (
        pytest_archon.archrule("RuleForModels", comment="Data models should not depend on other modules")
        .match(*modules_map["models"])
        .should_not_import("project.domains.*")
        .may_import(*modules_map["models"])
        .check("project.domains", skip_type_checking=True)
    )


def test_import_for_repo(modules_map, bussines_modules):
    """
    Repository Layer can import only other repositories and models of data.
    """
    (
        pytest_archon.archrule(
            "RuleForRepository", comment="Repository Layer can import only other repositories and models of data"
        )
        .match(*modules_map["repository"])
        .should_not_import(*bussines_modules)
        .check("project.domains", skip_type_checking=True)
    )


def test_import_for_helper_modules(modules_map, helper_modules):
    """In helper modules should not depend on modules of project."""
    (
        pytest_archon.archrule(
            "RuleForHelpersModules", comment="In helper modules should not depend on modules of project"
        )
        .match(*helper_modules)
        .should_not_import("project.domains.*")
        .may_import(*helper_modules)
        .check("project.domains", skip_type_checking=True)
    )


@pytest.mark.skip  # TODO: remove
def test_import_sqlalchemy(modules_map):
    """Do not write sql queries everywhere, only in repositories and data models."""
    (
        pytest_archon.archrule(
            "RuleForSqlalchemy", comment="Do not write sql queries everywhere, only in repositories and data models"
        )
        .match("project.*")
        .exclude("project.infrastructure.adapters.database", *modules_map["models"], *modules_map["repository"])
        .should_not_import("sqlalchemy")
        .check("project", skip_type_checking=True, only_direct_imports=True)
    )
