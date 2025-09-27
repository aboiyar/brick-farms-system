import importlib.util
import os
import sys
import types
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.core.security import TokenData, get_current_user
from app.db.session import get_db

# stub geoservice
sys.modules['app.services.geoservice'] = types.ModuleType('app.services.geoservice')

# load reports module
spec = importlib.util.spec_from_file_location('reports_module', os.path.join(os.path.dirname(__file__), '..', 'api', 'v1', 'reports.py'))
reports_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reports_module)

class DummyDB:
    class _Res:
        def __init__(self, rows=None):
            self._rows = rows or []
        def fetchall(self):
            return self._rows

    async def execute(self, sql, params=None):
        # rudimentary SQL pattern matching to return sample rows for tests
        s = str(sql).lower()
        if 'from yields' in s:
            # return 30 days of synthetic yields
            from datetime import datetime, timedelta
            rows = []
            now = datetime.utcnow()
            for i in range(30):
                ts = now - timedelta(days=i)
                class R: pass
                r = R()
                r.ts = ts
                r.yield_kg = 100.0 + i
                rows.append(r)
            return DummyDB._Res(list(reversed(rows)))
        if 'from activity' in s:
            class R: pass
            r = R()
            r.action = 'irrigation'
            r.cnt = 42
            return DummyDB._Res([r])
        # default empty
        return DummyDB._Res([])

    async def commit(self):
        return None


def make_app():
    db = DummyDB()
    app = FastAPI()
    app.include_router(reports_module.router, prefix='/api/v1/reports')
    import app.api.deps as deps_module
    app.dependency_overrides[deps_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[reports_module.tenant_scoped_user] = lambda: (TokenData(sub='u', tenant_id='t1', role='owner'), db)
    app.dependency_overrides[get_current_user] = lambda: TokenData(sub='u', tenant_id='t1', role='owner')
    app.dependency_overrides[get_db] = lambda: db
    return app


def test_forecast_and_export_csv():
    app = make_app()
    client = TestClient(app)
    r = client.get('/api/v1/reports/forecast')
    assert r.status_code == 200
    r2 = client.get('/api/v1/reports/export.csv')
    assert r2.status_code == 200
    assert r2.headers['content-type'].startswith('text/csv')
