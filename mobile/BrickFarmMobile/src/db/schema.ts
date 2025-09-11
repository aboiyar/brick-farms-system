// src/db/schema.ts
import { appSchema, tableSchema } from "@nozbe/watermelondb";

export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: "tasks",
      columns: [
        { name: "tenant_id", type: "string" },
        { name: "farm_id", type: "string", isIndexed: true },
        { name: "title", type: "string" },
        { name: "description", type: "string", isOptional: true },
        { name: "status", type: "string", isIndexed: true },
        { name: "assignee_id", type: "string", isOptional: true },
        { name: "due_at", type: "number", isOptional: true },
        { name: "latitude", type: "number", isOptional: true },
        { name: "longitude", type: "number", isOptional: true },
        { name: "created_at", type: "number" }
      ]
    }),
    tableSchema({
      name: "observations",
      columns: [
        { name: "tenant_id", type: "string" },
        { name: "plot_id", type: "string", isOptional: true },
        { name: "task_id", type: "string", isOptional: true },
        { name: "notes", type: "string", isOptional: true },
        { name: "metrics", type: "string", isOptional: true }, // JSON string
        { name: "latitude", type: "number", isOptional: true },
        { name: "longitude", type: "number", isOptional: true },
        { name: "photos", type: "string", isOptional: true }, // JSON array of local paths / keys
        { name: "uploaded", type: "boolean", isOptional: true },
        { name: "created_at", type: "number" }
      ]
    })
  ]
});
