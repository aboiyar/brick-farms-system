import React, { useEffect, useState } from "react";
import { fetchTasksWithGeom } from "./api/tasks";
import MapView from "./components/MapView";

function App() {
  const [tasks, setTasks] = useState<any>(null);

  useEffect(() => {
    fetchTasksWithGeom().then(setTasks);
  }, []);

  return (
    <div>
      <h2>BrickFarm Task Map</h2>
      <MapView tasks={tasks} />
    </div>
  );
}

export default App;
