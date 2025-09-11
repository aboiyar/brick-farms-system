import React, { useEffect, useRef } from "react";
import Map from "ol/Map";
import View from "ol/View";
import { Tile as TileLayer, Vector as VectorLayer } from "ol/layer";
import { OSM } from "ol/source";
import VectorSource from "ol/source/Vector";
import GeoJSON from "ol/format/GeoJSON";
import { Style, Fill, Stroke, Circle as CircleStyle, Text } from "ol/style";
import { fromLonLat } from "ol/proj";

import "ol/ol.css";
import "../styles/map.css";

interface MapViewProps {
  tasks: any; // GeoJSON FeatureCollection
}

export default function MapView({ tasks }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapObjRef = useRef<Map>();

  useEffect(() => {
    if (!mapRef.current) return;

    const base = new TileLayer({ source: new OSM() });

    const map = new Map({
      target: mapRef.current,
      layers: [base],
      view: new View({
        center: fromLonLat([8.0, 7.7]), // Benue default center
        zoom: 10,
      }),
    });

    mapObjRef.current = map;
    return () => map.setTarget(undefined);
  }, []);

  useEffect(() => {
    if (!mapObjRef.current) return;

    // clear old vector layers
    mapObjRef.current.getLayers().getArray().slice(1).forEach(layer => {
      mapObjRef.current?.removeLayer(layer);
    });

    if (tasks) {
      const vectorSource = new VectorSource({
        features: new GeoJSON().readFeatures(tasks, {
          featureProjection: "EPSG:3857",
        }),
      });

      const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: (feature) => {
          const type = feature.getGeometry()?.getType();
          if (type === "Polygon" || type === "MultiPolygon") {
            return new Style({
              stroke: new Stroke({ color: "#2E7D32", width: 2 }),
              fill: new Fill({ color: "rgba(46,125,50,0.3)" }),
              text: new Text({
                text: feature.get("title") || "Plot",
                fill: new Fill({ color: "#000" }),
                stroke: new Stroke({ color: "#fff", width: 2 }),
              }),
            });
          }
          if (type === "Point") {
            return new Style({
              image: new CircleStyle({
                radius: 6,
                fill: new Fill({ color: "#1565C0" }),
                stroke: new Stroke({ color: "#fff", width: 2 }),
              }),
              text: new Text({
                text: feature.get("title") || "Task",
                offsetY: -12,
                fill: new Fill({ color: "#000" }),
                stroke: new Stroke({ color: "#fff", width: 2 }),
              }),
            });
          }
          return undefined;
        },
      });

      mapObjRef.current.addLayer(vectorLayer);
    }
  }, [tasks]);

  return <div ref={mapRef} className="map-container"></div>;
}
