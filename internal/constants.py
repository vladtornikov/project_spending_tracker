from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class RabbitTasksConstant(StrEnum):
    REPORTS_CATEGORY = "reports.generate.monthly_by_category"
    BEAT_DELETE_TRANSACTION = 'beat.delete.old.transactions'
