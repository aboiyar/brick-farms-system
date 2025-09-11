// src/App.tsx
import React, { useEffect } from "react";
import { SafeAreaView, Text } from "react-native";
import { db } from "./db/database";
import BackgroundFetch from "react-native-background-fetch";
import { processPendingObservations } from "./services/uploads";
import TasksScreen from "./screens/TasksScreen";

export default function App(){
  useEffect(() => {
    // configure background fetch
    BackgroundFetch.configure({
      minimumFetchInterval: 15,
      stopOnTerminate: false,
      startOnBoot: true,
    }, async (taskId) => {
      console.log("[BackgroundFetch] taskId:", taskId);
      try {
        await processPendingObservations();
      } catch (e) {
        console.warn("Background sync error", e);
      }
      BackgroundFetch.finish(taskId);
    }, (error) => {
      console.warn("[BackgroundFetch] failed to start", error);
    });

    return () => {
      BackgroundFetch.stop();
    };
  }, []);

  return (
    <SafeAreaView style={{flex:1}}>
      <TasksScreen />
    </SafeAreaView>
  );
}
