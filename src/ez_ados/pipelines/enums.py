"""Enumerations for Pipelines types."""

from ..base.enums import StrIntEnum


class ConfigurationType(StrIntEnum):
    """
    Enum for available configuration types.

    Reference: https://learn.microsoft.com/en-us/javascript/api/azure-devops-extension-api/configurationtype
    """

    unknown = 0
    yaml = 1
    designerHyphenJson = 2
    designerJson = 2
    justInTime = 3
