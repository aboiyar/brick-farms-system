// src/db/database.ts
import { Database } from "@nozbe/watermelondb";
import SQLiteAdapter from "@nozbe/watermelondb/adapters/sqlite";
import { schema } from "./schema";
import Task from "./models/Task";
import Observation from "./models/Observation";

const adapter = new SQLiteAdapter({
  dbName: "brickfarm",
  schema
});

export const db = new Database({
  adapter,
  modelClasses: [Task, Observation],
  actionsEnabled: true
});
