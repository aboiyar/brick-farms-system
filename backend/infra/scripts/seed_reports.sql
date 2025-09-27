-- Seed realistic-ish activity and yields time-series across multiple farms/plots
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS activity (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id uuid,
  farm_id uuid,
  plot_id uuid,
  action text,
  ts timestamptz
);

CREATE TABLE IF NOT EXISTS yields (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id uuid,
  farm_id uuid,
  plot_id uuid,
  crop text,
  ts timestamptz,
  yield_kg numeric
);

-- Create 3 farms, each with 2 plots, and seed daily activities and quarterly yields for the last 24 months
DO $$
DECLARE
  f uuid;
  p uuid;
  tenant uuid := gen_random_uuid();
  start_ts timestamptz := now() - interval '730 days';
  d timestamptz;
  crop text := 'maize';
BEGIN
  FOR i IN 1..3 LOOP
    f := gen_random_uuid();
    FOR j IN 1..2 LOOP
      p := gen_random_uuid();
      -- daily activities: irrigation every 7 days, maintenance every 30 days, planting/harvest events
      d := start_ts;
      WHILE d < now() LOOP
        IF (extract(day from d)::int % 7 = 0) THEN
          INSERT INTO activity (tenant_id, farm_id, plot_id, action, ts) VALUES (tenant, f, p, 'irrigation', d);
        END IF;
        IF (extract(day from d)::int % 30 = 0) THEN
          INSERT INTO activity (tenant_id, farm_id, plot_id, action, ts) VALUES (tenant, f, p, 'maintenance', d);
        END IF;
        d := d + interval '1 day';
      END LOOP;
      -- quarterly yields (every ~90 days)
      d := start_ts;
      WHILE d < now() LOOP
        INSERT INTO yields (tenant_id, farm_id, plot_id, crop, ts, yield_kg) VALUES (tenant, f, p, crop, d + interval '89 days', (random()*500 + 200)::numeric);
        d := d + interval '90 days';
      END LOOP;
    END LOOP;
  END LOOP;
END$$;

-- small convenience index for faster reporting queries
CREATE INDEX IF NOT EXISTS idx_activity_ts ON activity (ts);
CREATE INDEX IF NOT EXISTS idx_yields_ts ON yields (ts);

