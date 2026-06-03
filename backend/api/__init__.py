"""API路由模块"""
from .groups import router as groups_router
from .matches import router as matches_router
from .simulation import router as simulation_router
from .history import router as history_router

__all__ = ["groups_router", "matches_router", "simulation_router", "history_router"]