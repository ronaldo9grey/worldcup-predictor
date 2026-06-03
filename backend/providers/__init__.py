"""数据提供者模块 - 可扩展的数据源抽象"""
from .base import DataProvider
from .h2h_provider import H2HProvider
from .team_value_provider import TeamValueProvider
from .wc_history_provider import WCHistoryProvider
from .form_provider import FormProvider

__all__ = [
    "DataProvider",
    "H2HProvider",
    "TeamValueProvider",
    "WCHistoryProvider",
    "FormProvider"
]
