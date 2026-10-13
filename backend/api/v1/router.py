"""
Router central para la versión 1 de la API (v1).
"""

from fastapi import APIRouter
from backend.api.v1.endpoints import tickets

api_v1_router = APIRouter()
api_v1_router.include_router(tickets.router)
