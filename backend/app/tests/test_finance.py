import importlib.util
import os
import sys
import types
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.db.session import get_db

# stub geoservice to avoid heavy imports
sys.modules['app.services.geoservice'] = types.ModuleType('app.services.geoservice')

# load finance module directly
spec = importlib.util.spec_from_file_location('finance_module', os.path.join(os.path.dirname(__file__), '..', 'api', 'v1', 'finance.py'))
finance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finance_module)

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


def make_app_with_db(row):
    db = DummyDB(row=row)
    app = FastAPI()
    app.include_router(finance_module.router, prefix='/api/v1/finance')
    # override dependencies
    import app.api.deps as deps_module
    app.dependency_overrides[deps_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[finance_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[get_current_user] = lambda: TokenData(sub='u', tenant_id='t1', role='owner')
    app.dependency_overrides[get_db] = lambda: db
    return app, db


def test_create_transaction():
    row = DummyRow(id='11111111-1111-1111-1111-111111111111', account_id='11111111-1111-1111-1111-111111111112', amount=100.0, currency='NGN', ts='2025-09-27T00:00:00Z', description='expense', meta=None)
    app, db = make_app_with_db(row)
    client = TestClient(app)
    payload = {"account_id": "11111111-1111-1111-1111-111111111112", "amount": 100.0}
    r = client.post('/api/v1/finance/transactions', json=payload)
    assert r.status_code == 201


def test_create_investment_and_roi():
    inv_row = DummyRow(id='22222222-2222-2222-2222-222222222222', name='Farm expansion', amount=1000.0, currency='NGN', ts='2025-09-01T00:00:00Z', meta={})
    payout_row = DummyRow(total=1200.0)
    # MultiDB returns rows in sequence for each execute call
    class MultiDB(DummyDB):
        def __init__(self, rows):
            self._rows = list(rows)
        async def execute(self, sql, params=None):
            if not self._rows:
                return DummyResult(None)
            return DummyResult(self._rows.pop(0))

    # 1) Test create investment (simple DummyDB returning inv_row)
    app1, db1 = make_app_with_db(inv_row)
    client1 = TestClient(app1)
    payload = {"name": "Farm expansion", "amount": 1000.0}
    r = client1.post('/api/v1/finance/investments', json=payload)
    assert r.status_code == 201

    # 2) Test ROI with a fresh app and MultiDB that returns inv_row then payout_row
    db2 = MultiDB([inv_row, payout_row])
    app2 = FastAPI()
    app2.include_router(finance_module.router, prefix='/api/v1/finance')
    import app.api.deps as deps_module
    app2.dependency_overrides[deps_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db2)
    app2.dependency_overrides[finance_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db2)
    app2.dependency_overrides[get_current_user] = lambda: TokenData(sub='u', tenant_id='t1', role='owner')
    app2.dependency_overrides[get_db] = lambda: db2
    client2 = TestClient(app2)
    r2 = client2.get(f'/api/v1/finance/investments/{inv_row.id}/roi')
    assert r2.status_code == 200
    data = r2.json()
    assert 'roi' in data
