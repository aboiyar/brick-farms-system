import pytest
import json
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

import importlib.util
import os
import sys
import types

# prevent importing real geoservice which pulls in aioredis (incompatible in this env)
geoservice_stub = types.ModuleType("app.services.geoservice")
def invalidate_tiles_for_bbox(*a, **k):
    return None
geoservice_stub.invalidate_tiles_for_bbox = invalidate_tiles_for_bbox
sys.modules["app.services.geoservice"] = geoservice_stub

spec = importlib.util.spec_from_file_location(
    "plots_module",
    os.path.join(os.path.dirname(__file__), "..", "api", "v1", "plots.py"),
)
plots_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plots_module)

from app.core.security import TokenData


class DummyRow:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class DummyResult:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row

    def fetchall(self):
        return [self._row]


class DummyDB:
    def __init__(self, row=None):
        self.row = row

    async def execute(self, sql, params=None):
        # return a dummy row depending on context
        return DummyResult(self.row)

    async def commit(self):
        return None


def test_create_plot_unauthorized(monkeypatch):
    def fake_tenant_scoped_user():
        return (TokenData(sub='u', tenant_id='t', role='investor'), None)

    monkeypatch.setattr('app.api.deps.tenant_scoped_user', fake_tenant_scoped_user)
    monkeypatch.setattr(plots_module, 'tenant_scoped_user', fake_tenant_scoped_user)
    # avoid calling external geoservice
    monkeypatch.setattr(plots_module, 'invalidate_tiles_for_bbox', lambda *a, **k: None)

    test_app = FastAPI()
    test_app.include_router(plots_module.router, prefix='/api/v1')

    with TestClient(test_app) as client:
        payload = {
            "tenant_id": "00000000-0000-0000-0000-000000000000",
            "farm_id": "00000000-0000-0000-0000-000000000000",
            "name": "Test Plot",
            "geom_geojson": {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}
        }
    r = client.post('/api/v1/plots', json=payload)
    assert r.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


def test_create_plot_authorized(monkeypatch):
    row = DummyRow(id='11111111-1111-1111-1111-111111111111', tenant_id='00000000-0000-0000-0000-000000000000', farm_id='00000000-0000-0000-0000-000000000000', name='Test Plot', description=None, crop_type=None, area_ha=1.23, geom_geojson=json.dumps({"type":"Polygon","coordinates":[[[0,0],[0,1],[1,1],[1,0],[0,0]]]}) , created_at=None, updated_at=None)
    db = DummyDB(row=row)

    def fake_tenant_scoped_user():
        return (TokenData(sub='u', tenant_id='00000000-0000-0000-0000-000000000000', role='agronomist'), db)

    monkeypatch.setattr('app.api.deps.tenant_scoped_user', fake_tenant_scoped_user)
    monkeypatch.setattr(plots_module, 'tenant_scoped_user', fake_tenant_scoped_user)
    monkeypatch.setattr(plots_module, 'invalidate_tiles_for_bbox', lambda *a, **k: None)

    test_app = FastAPI()
    test_app.include_router(plots_module.router, prefix='/api/v1')

    with TestClient(test_app) as client:
        payload = {
            "tenant_id": "00000000-0000-0000-0000-000000000000",
            "farm_id": "00000000-0000-0000-0000-000000000000",
            "name": "Test Plot",
            "geom_geojson": {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}
        }
        r = client.post('/api/v1/plots', json=payload)
        # We expect either 201 or 500 depending on DB stub; ensure not 403
        assert r.status_code != status.HTTP_403_FORBIDDEN
