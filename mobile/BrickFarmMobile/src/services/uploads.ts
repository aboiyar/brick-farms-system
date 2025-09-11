// src/services/uploads.ts
import api from "./api";
import RNFetchBlob from "rn-fetch-blob";
import { db } from "../db/database";

export async function getPresign(filename: string, contentType: string, purpose="observation"){
  const res = await api.post("/presign", { filename, content_type: contentType, purpose });
  return res.data;
}

export async function uploadFileToPresign(upload_url: string, localPath: string, contentType: string){
  // Use RNFetchBlob for robust PUT
  const res = await RNFetchBlob.fetch('PUT', upload_url, {
    'Content-Type': contentType
  }, RNFetchBlob.wrap(localPath));
  if (res.info().status >= 200 && res.info().status < 300) return true;
  throw new Error("Upload failed");
}

export async function registerUpload(key: string, observation_id: string | null){
  const res = await api.post("/register", { key, observation_id });
  return res.data;
}

/**
 * Process pending observations:
 *  - for each local photo file, presign -> upload -> register
 *  - on success mark observation as uploaded
 */
export async function processPendingObservations(){
  const observationsCollection = db.collections.get("observations");
  const pending = await observationsCollection.query().fetch();
  for (const obs of pending) {
    const obj = obs._raw; // use raw for speed; or obs.get()
    if (obj.uploaded) continue;
    const photos = obj.photos ? JSON.parse(obj.photos) : [];
    const uploadedKeys = [];
    try {
      for (const localPath of photos) {
        const fname = localPath.split("/").pop() || `photo-${Date.now()}.jpg`;
        const pres = await getPresign(fname, "image/jpeg", "observation");
        await uploadFileToPresign(pres.upload_url, localPath, "image/jpeg");
        const reg = await registerUpload(pres.key, obj.id);
        uploadedKeys.push(reg.photo_report_id);
      }
      await db.action(async () => {
        const rec = await observationsCollection.find(obj.id);
        await rec.update(r => {
          r.uploaded = true;
          // replace photos URIs with remote keys if you want. For now keep as-is.
        });
      });
    } catch (e) {
      console.warn("Upload failed for obs", obj.id, e);
      // leave for next sync
    }
  }
}
