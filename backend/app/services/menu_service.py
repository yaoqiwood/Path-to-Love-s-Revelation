from typing import List, Optional, Annotated
from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import SystemMenu
from app.schemas.user_schema import MenuCreate, MenuUpdate, MenuResponse
from app.repository import MenuRepository


class MenuService:
    def __init__(self, db: AsyncSession):
        self.repo = MenuRepository(db)

    def _build_tree(
        self, all_menus: List[SystemMenu], pid: int = 0
    ) -> List[MenuResponse]:
        tree = []
        for menu in all_menus:
            if menu.pid == pid:
                node = MenuResponse.model_validate(menu)
                children = self._build_tree(all_menus, menu.id)
                if children:
                    node.children = children
                tree.append(node)
        return tree

    async def get_menu_tree(self) -> List[MenuResponse]:
        """获取菜单树形结构"""
        all_menus = await self.repo.get_all()
        return self._build_tree(all_menus)

    async def list_menus(
        self, menu_name: Optional[str] = None, menu_type: Optional[str] = None
    ) -> List[MenuResponse]:
        """获取菜单列表（平铺，支持筛选）"""
        menus = await self.repo.get_all(menu_name=menu_name, menu_type=menu_type)
        return self._build_tree(menus)

    async def get_menu(self, menu_id: int) -> MenuResponse:
        """获取菜单详情"""
        menu = await self.repo.get_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail="菜单不存在")
        return MenuResponse.model_validate(menu)

    async def create_menu(self, data: MenuCreate, username: str) -> MenuResponse:
        """新增菜单"""
        menu = SystemMenu(
            pid=data.pid,
            menu_type=data.menu_type,
            menu_name=data.menu_name,
            menu_icon=data.menu_icon or "",
            menu_sort=data.menu_sort,
            perms=data.perms or "",
            paths=data.paths or "",
            component=data.component or "",
            selected=data.selected or "",
            params=data.params or "",
            cache_status=data.cache_status,
            show_status=data.show_status,
            enable_status=data.enable_status,
            create_time=datetime.now(),
            create_by=username,
        )
        menu = await self.repo.create(menu)
        return MenuResponse.model_validate(menu)

    async def update_menu(
        self, menu_id: int, data: MenuUpdate, username: str
    ) -> MenuResponse:
        """更新菜单"""
        menu = await self.repo.get_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail="菜单不存在")

        # 不能将自身设为上级
        if data.pid is not None and data.pid == menu_id:
            raise HTTPException(status_code=400, detail="上级菜单不能选择自身")

        update_fields = data.model_dump(exclude_unset=True)
        update_fields["update_time"] = datetime.now()
        update_fields["update_by"] = username

        menu = await self.repo.update(menu, update_fields)
        return MenuResponse.model_validate(menu)

    async def delete_menu(self, menu_id: int) -> dict:
        """删除菜单（同时删除子菜单）"""
        menu = await self.repo.get_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail="菜单不存在")

        # 检查是否有子菜单
        children = await self.repo.get_children(menu_id)
        if children:
            raise HTTPException(status_code=400, detail="存在子菜单，不允许删除")

        await self.repo.delete(menu)
        return {"message": "删除成功"}


async def get_menu_service(db: AsyncSession = Depends(get_db)) -> MenuService:
    return MenuService(db)


MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]
