// src/screens/CaptureObservation.tsx
import React from "react";
import { View, Button, Alert } from "react-native";
import ImagePicker from "react-native-image-crop-picker";
import { db } from "../db/database";
import { Q } from "@nozbe/watermelondb";

export default function CaptureObservation({ route }: any) {
  const { plotId, taskId, tenantId } = route.params || {};

  async function takePhotoAndSave() {
    try {
      const image = await ImagePicker.openCamera({ cropping: false, compressImageQuality: 0.8 });
      const localPath = image.path;
      const id = `${Date.now()}-${Math.random().toString(36).slice(2,8)}`;

      const observations = db.collections.get("observations");
      await db.action(async () => {
        await observations.create(o => {
          o._raw.id = id;
          o.tenant_id = tenantId;
          o.plot_id = plotId;
          o.task_id = taskId;
          o.photos = JSON.stringify([localPath]);
          o.uploaded = false;
          o.created_at = Date.now();
        });
      });
      Alert.alert("Saved", "Observation saved locally and will be uploaded when online.");
    } catch (e) {
      console.warn(e);
      Alert.alert("Error", "Could not capture photo");
    }
  }

  return (
    <View style={{padding:16}}>
      <Button title="Take Photo" onPress={takePhotoAndSave} />
    </View>
  );
}
