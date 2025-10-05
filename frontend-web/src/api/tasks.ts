import { api } from "./client"

export async function fetchTasksWithGeom() {
  return api.get('/tasks?include_geom=true')
}
