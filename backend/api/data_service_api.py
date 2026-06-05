"""
数据服务 API 示例
展示如何在现有系统中集成 DataService
"""
from fastapi import APIRouter, Query
from typing import Dict, List, Optional

from services.data_service import get_data_service

router = APIRouter(prefix="/api/data", tags=["数据服务"])


@router.get("/source")
async def get_source_info() -> Dict:
    """
    获取当前数据源信息
    """
    ds = get_data_service()
    return await ds.health_check()


@router.get("/teams")
async def get_teams() -> List[Dict]:
    """
    获取所有球队
    """
    ds = get_data_service()
    return await ds.get_all_teams()


@router.get("/teams/{code}")
async def get_team(code: str) -> Dict:
    """
    获取单个球队
    """
    ds = get_data_service()
    team = await ds.get_team(code)
    if not team:
        return {"error": f"Team {code} not found"}
    return team


@router.get("/groups")
async def get_groups() -> Dict[str, List[Dict]]:
    """
    获取所有小组球队
    """
    ds = get_data_service()
    return await ds.get_all_groups()


@router.get("/groups/{group}")
async def get_group_teams(group: str) -> List[Dict]:
    """
    获取小组球队
    """
    ds = get_data_service()
    return await ds.get_group_teams(group)


@router.get("/matches")
async def get_matches(
    group: Optional[str] = Query(None, description="小组名称"),
    status: Optional[str] = Query(None, description="比赛状态")
) -> List[Dict]:
    """
    获取比赛列表
    """
    ds = get_data_service()
    return await ds.get_matches(group=group, status=status)


@router.get("/standings/{group}")
async def get_standings(group: str) -> List[Dict]:
    """
    获取小组积分榜
    """
    ds = get_data_service()
    return await ds.get_standings(group)


@router.get("/rankings")
async def get_rankings() -> Dict[str, int]:
    """
    获取FIFA排名
    """
    ds = get_data_service()
    return await ds.get_fifa_rankings()


@router.post("/refresh")
async def refresh_data() -> Dict:
    """
    手动刷新数据
    """
    ds = get_data_service()
    success = await ds.refresh()
    return {
        "success": success,
        "message": "数据刷新成功" if success else "数据刷新失败"
    }


@router.post("/switch-source")
async def switch_source(
    source_type: str = Query(..., description="数据源类型: mock, balldontlie"),
    api_key: Optional[str] = Query(None, description="API Key")
) -> Dict:
    """
    切换数据源
    """
    ds = get_data_service()
    
    kwargs = {}
    if api_key:
        kwargs["api_key"] = api_key
    
    success = await ds.switch_source(source_type, **kwargs)
    
    return {
        "success": success,
        "current_source": ds.source_name,
        "message": f"已切换到 {source_type}" if success else f"切换失败"
    }