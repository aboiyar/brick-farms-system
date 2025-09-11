// src/db/models/Observation.ts
import { Model } from "@nozbe/watermelondb";
import { field } from "@nozbe/watermelondb/decorators";

export default class Observation extends Model {
  static table = "observations";
  @field("notes") notes!: string;
  @field("metrics") metrics!: string;
  @field("photos") photos!: string;
  @field("uploaded") uploaded!: boolean;
  @field("created_at") createdAt!: number;
}
