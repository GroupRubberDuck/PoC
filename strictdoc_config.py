from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Tracciabilità Use Cases del PoC",
        project_features=[
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            "SOURCE_FILE_LANGUAGE_PARSERS",
        ],
        statistics_generator="docs.sdoc_project_statistics.SDocStatisticsGenerator",
    )
    return config
