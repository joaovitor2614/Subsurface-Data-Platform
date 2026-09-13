from fastapi import FastAPI

from . import auth, users, files, folders


routers_info = [
    {"router": users.router, "prefix": "/api/users"},
    {"router": auth.router, "prefix": "/api/auth"},
]


def register_routers(app: FastAPI) -> None:
    for route_info in routers_info:
        app.include_router(
            route_info["router"],
            prefix=route_info["prefix"],
        )
