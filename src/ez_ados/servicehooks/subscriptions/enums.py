"""Enumerations for Service Hooks' Subscriptions types."""

from ...base.enums import StrIntEnum


class SubscriptionStatus(StrIntEnum):
    """
    Enum for available hook subscriptions states types.

    Reference: https://learn.microsoft.com/en-us/javascript/api/azure-devops-extension-api/subscriptionstatus
    """

    enabled = 0
    onProbation = 10
    disabledByUser = 20
    disabledBySystem = 30
    disabledByInactiveIdentity = 40
