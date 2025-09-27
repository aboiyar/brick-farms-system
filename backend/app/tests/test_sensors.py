import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
import importlib.util
import os
import sys
import types
from app.db.session import get_db

# stub geoservice to avoid redis import in tests
geoservice_stub = types.ModuleType("app.services.geoservice")
def invalidate_tiles_for_bbox(*a, **k):
    return None
geoservice_stub.invalidate_tiles_for_bbox = invalidate_tiles_for_bbox
sys.modules["app.services.geoservice"] = geoservice_stub

# load sensors module directly to avoid package side-effects
spec = importlib.util.spec_from_file_location(
    "sensors_module",
    os.path.join(os.path.dirname(__file__), "..", "api", "v1", "sensors.py"),
)
sensors_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sensors_module)

from app.core.security import TokenData, get_current_user

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
        return DummyResult(self.row)
    async def commit(self):
        return None


def test_ingest_missing_api_key(monkeypatch):
    # device exists but api_key is 'secret'
    row = DummyRow(api_key='secret', tenant_id='t1')
    db = DummyDB(row=row)

    async def fake_get_db():
        yield db

    monkeypatch.setattr('app.api.deps.tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))
    monkeypatch.setattr(sensors_module, 'tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))

    app = FastAPI()
    app.include_router(sensors_module.router, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: db
    # override both the original dependency and the one captured in sensors_module
    import app.api.deps as deps_module
    app.dependency_overrides[deps_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[sensors_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    # also override get_current_user used inside set_tenant_context to avoid OAuth checks
    app.dependency_overrides[get_current_user] = lambda: TokenData(sub='u', tenant_id='t1', role='owner')
    client = TestClient(app)

    payload = {
        "device_id": "11111111-1111-1111-1111-111111111111",
        "metric": "temp",
        "value": 23.4
    }
    r = client.post('/api/v1/readings', json=payload)
    assert r.status_code == 403


def test_ingest_with_api_key(monkeypatch):
    row = DummyRow(api_key='secret', tenant_id='t1')
    db = DummyDB(row=row)

    async def fake_get_db():
        yield db

    monkeypatch.setattr('app.api.deps.tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))
    monkeypatch.setattr(sensors_module, 'tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))

    app = FastAPI()
    app.include_router(sensors_module.router, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: db
    import app.api.deps as deps_module
    app.dependency_overrides[deps_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[sensors_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[get_current_user] = lambda: TokenData(sub='u', tenant_id='t1', role='owner')
    client = TestClient(app)

    payload = {
        "device_id": "11111111-1111-1111-1111-111111111111",
        "metric": "temp",
        "value": 23.4
    }
    r = client.post('/api/v1/readings', json=payload, headers={"X-API-KEY": "secret"})
    # we return created id; the DB stub returns a DummyResult so id may be None, ensure allowed
    assert r.status_code == 201


def test_update_device(monkeypatch):
    # prepare row to be returned by update
    row = DummyRow(id='11111111-1111-1111-1111-111111111111', farm_id='11111111-1111-1111-1111-111111111112', plot_id=None, name='Old', protocol='http', api_key='secret')
    db = DummyDB(row=row)

    monkeypatch.setattr('app.api.deps.tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))
    monkeypatch.setattr(sensors_module, 'tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))

    async def fake_get_db():
        yield db

    app = FastAPI()
    app.include_router(sensors_module.router, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: db
    import app.api.deps as deps_module
    app.dependency_overrides[deps_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[sensors_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[get_current_user] = lambda: TokenData(sub='u', tenant_id='t1', role='owner')
    client = TestClient(app)

    payload = {"name": "New"}
    r = client.patch('/api/v1/devices/11111111-1111-1111-1111-111111111111', json=payload)
    assert r.status_code == 200


def test_delete_device(monkeypatch):
    row = DummyRow(id='11111111-1111-1111-1111-111111111111')
    db = DummyDB(row=row)

    monkeypatch.setattr('app.api.deps.tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))
    monkeypatch.setattr(sensors_module, 'tenant_scoped_user', lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db))

    app = FastAPI()
    app.include_router(sensors_module.router, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: db
    import app.api.deps as deps_module
    app.dependency_overrides[deps_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[sensors_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[get_current_user] = lambda: TokenData(sub='u', tenant_id='t1', role='owner')
    client = TestClient(app)

    r = client.delete('/api/v1/devices/11111111-1111-1111-1111-111111111111')
    assert r.status_code == 204
