import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "https://api.brickservers.ng/api/v1";

export async function fetchTasksWithGeom() {
  const res = await axios.get(`${API_BASE}/tasks?include_geom=true`);
  return res.data; // should be FeatureCollection
}
