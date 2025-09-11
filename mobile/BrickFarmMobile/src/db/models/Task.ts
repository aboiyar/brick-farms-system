// src/db/models/Task.ts
import { Model } from "@nozbe/watermelondb";
import { field } from "@nozbe/watermelondb/decorators";

export default class Task extends Model {
  static table = "tasks";
  @field("title") title!: string;
  @field("description") description!: string;
  @field("status") status!: string;
  @field("created_at") createdAt!: number;
}
