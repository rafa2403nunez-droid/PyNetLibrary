import * as THREE from "three";
import * as OBC from "@thatopen/components";
import * as OBF from "@thatopen/components-front";
import * as BUI from "@thatopen/ui";
import { viewportGridTemplate } from "./ui-templates/grids/viewport";
import { viewportSettingsTemplate } from "./ui-templates/buttons/viewport-settings";
import { getConfig } from "./config";
import { loadModelFromUrl, loadAllModels } from "./loader";

BUI.Manager.init();

// Components Setup

const components = new OBC.Components();
const worlds = components.get(OBC.Worlds);

const world = worlds.create<
  OBC.SimpleScene,
  OBC.OrthoPerspectiveCamera,
  OBF.PostproductionRenderer
>();

world.name = "Main";
world.scene = new OBC.SimpleScene(components);
world.scene.setup();
world.scene.three.background = new THREE.Color(0x1a1d23);

const viewport = BUI.Component.create<BUI.Viewport>(() => {
  return BUI.html`<bim-viewport></bim-viewport>`;
});

// Mount viewport to DOM BEFORE creating renderer — otherwise framebuffers init at 0x0
const app = document.getElementById("app")!;
app.style.display = "flex";
app.style.width = "100%";
app.style.height = "100vh";
viewport.style.flex = "1";
viewport.style.width = "100%";
viewport.style.height = "100%";
app.appendChild(viewport);

world.renderer = new OBF.PostproductionRenderer(components, viewport);
world.camera = new OBC.OrthoPerspectiveCamera(components);
world.camera.threePersp.near = 0.01;
world.camera.threePersp.updateProjectionMatrix();
world.camera.controls.restThreshold = 0.05;

const worldGrid = components.get(OBC.Grids).create(world);
worldGrid.material.uniforms.uColor.value = new THREE.Color(0x494b50);
worldGrid.material.uniforms.uSize1.value = 2;
worldGrid.material.uniforms.uSize2.value = 8;

const resizeWorld = () => {
  world.renderer?.resize();
  world.camera.updateAspect();
};

viewport.addEventListener("resize", resizeWorld);

world.dynamicAnchor = false;

components.init();

components.get(OBC.Raycasters).get(world);

const { postproduction } = world.renderer;
postproduction.enabled = true;
postproduction.style = OBF.PostproductionAspect.COLOR_SHADOWS;

const { aoPass, edgesPass } = world.renderer.postproduction;

edgesPass.color = new THREE.Color(0x494b50);

const aoParameters = {
  radius: 0.25,
  distanceExponent: 1,
  thickness: 1,
  scale: 1,
  samples: 16,
  distanceFallOff: 1,
  screenSpaceRadius: true,
};

const pdParameters = {
  lumaPhi: 10,
  depthPhi: 2,
  normalPhi: 3,
  radius: 4,
  radiusExponent: 1,
  rings: 2,
  samples: 16,
};

aoPass.updateGtaoMaterial(aoParameters);
aoPass.updatePdMaterial(pdParameters);

const fragments = components.get(OBC.FragmentsManager);
fragments.init("./worker/worker.mjs");

fragments.core.models.materials.list.onItemSet.add(({ value: material }) => {
  const isLod = "isLodMaterial" in material && material.isLodMaterial;
  if (isLod) {
    world.renderer!.postproduction.basePass.isolatedMaterials.push(material);
  }
});

world.camera.projection.onChanged.add(() => {
  for (const [_, model] of fragments.list) {
    model.useCamera(world.camera.three);
  }
});

world.camera.controls.addEventListener("rest", () => {
  fragments.core.update(true);
});

const ifcLoader = components.get(OBC.IfcLoader);
await ifcLoader.setup({
  autoSetWasm: false,
  wasm: { absolute: true, path: "https://unpkg.com/web-ifc@0.0.71/" },
});

const highlighter = components.get(OBF.Highlighter);
highlighter.setup({
  world,
  selectMaterialDefinition: {
    color: new THREE.Color("#bcf124"),
    renderedFaces: 1,
    opacity: 1,
    transparent: false,
  },
});

// Clipper Setup
const clipper = components.get(OBC.Clipper);
viewport.ondblclick = () => {
  if (clipper.enabled) clipper.create(world);
};

window.addEventListener("keydown", (event) => {
  if (event.code === "Delete" || event.code === "Backspace") {
    clipper.delete(world);
  }
});

// Length Measurement Setup
const lengthMeasurer = components.get(OBF.LengthMeasurement);
lengthMeasurer.world = world;
lengthMeasurer.color = new THREE.Color("#6528d7");

lengthMeasurer.list.onItemAdded.add((line) => {
  const center = new THREE.Vector3();
  line.getCenter(center);
  const radius = line.distance() / 3;
  const sphere = new THREE.Sphere(center, radius);
  world.camera.controls.fitToSphere(sphere, true);
});

viewport.addEventListener("dblclick", () => lengthMeasurer.create());

window.addEventListener("keydown", (event) => {
  if (event.code === "Delete" || event.code === "Backspace") {
    lengthMeasurer.delete();
  }
});

// Area Measurement Setup
const areaMeasurer = components.get(OBF.AreaMeasurement);
areaMeasurer.world = world;
areaMeasurer.color = new THREE.Color("#6528d7");

areaMeasurer.list.onItemAdded.add((area) => {
  if (!area.boundingBox) return;
  const sphere = new THREE.Sphere();
  area.boundingBox.getBoundingSphere(sphere);
  world.camera.controls.fitToSphere(sphere, true);
});

viewport.addEventListener("dblclick", () => {
  areaMeasurer.create();
});

window.addEventListener("keydown", (event) => {
  if (event.code === "Enter" || event.code === "NumpadEnter") {
    areaMeasurer.endCreation();
  }
});

// Define what happens when a fragments model has been loaded
fragments.list.onItemSet.add(async ({ value: model }) => {
  model.useCamera(world.camera.three);
  model.getClippingPlanesEvent = () => {
    return Array.from(world.renderer!.three.clippingPlanes) || [];
  };
  world.scene.three.add(model.object);
  await fragments.core.update(true);
  await world.camera.fitToItems();
});

// Viewport Layouts
const [viewportSettings] = BUI.Component.create(viewportSettingsTemplate, {
  components,
  world,
});

viewport.append(viewportSettings);

const [viewportGrid] = BUI.Component.create(viewportGridTemplate, {
  components,
  world,
});

viewport.append(viewportGrid);

// Viewport already mounted above (before renderer init)

// ─── Public API for external control (iframe postMessage / parent page) ───

declare global {
  interface Window {
    loadModel: (url: string, name?: string) => Promise<void>;
    highlightElements: (
      modelId: string,
      expressIds: number[],
    ) => Promise<void>;
    fitToAllModels: () => Promise<void>;
  }
}

// Expose loadModel globally (used by ViewerDashboard.py pattern)
window.loadModel = async (url: string, name?: string) => {
  await loadModelFromUrl(ifcLoader, url, name);
};

// Expose highlight for clash navigation
window.highlightElements = async (
  modelId: string,
  expressIds: number[],
) => {
  const selection: OBC.ModelIdMap = {};
  selection[modelId] = new Set(expressIds);
  await highlighter.highlightByID("select", selection, true, true);
};

// Expose fit to all
window.fitToAllModels = async () => {
  await world.camera.fitToItems();
};

// Listen for postMessage from parent (dashboard iframe communication)
window.addEventListener("message", async (event) => {
  if (!event.data || event.data.type !== "viewer-command") return;

  const { action, payload } = event.data;

  switch (action) {
    case "loadModel":
      await window.loadModel(payload.url, payload.name);
      break;
    case "highlightElements":
      await window.highlightElements(payload.modelId, payload.expressIds);
      break;
    case "fitToAllModels":
      await window.fitToAllModels();
      break;
    case "clearHighlight":
      await highlighter.clear("select");
      break;
  }
});

// ─── Auto-load models from config ───

const config = getConfig();

if (config.autoLoad && config.modelUrls.length > 0) {
  loadAllModels(config, ifcLoader, (loaded, total, name) => {
    console.log(
      `[PyNET Viewer] Progress: ${loaded}/${total} — ${name}`,
    );
  }).then(() => {
    console.log("[PyNET Viewer] All models loaded");
    world.camera.fitToItems();
    window.parent?.postMessage(
      { type: "viewer-event", event: "modelsLoaded" },
      "*",
    );
  });
}
