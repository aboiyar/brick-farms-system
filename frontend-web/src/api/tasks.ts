import { api } from "./client"

// Backend returns a list of task records with an optional `location` GeoJSON object
// Convert to a GeoJSON FeatureCollection so MapView can consume it directly.
export async function fetchTasksWithGeom() {
  const rows: any[] = await api.get('/tasks')
  const features = rows.map(r => ({
    type: 'Feature',
    geometry: r.location || null,
    properties: { ...r, location: undefined }
  }))
  return { type: 'FeatureCollection', features }
}
