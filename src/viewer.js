import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

// 默认示例模型；可在调用时传入新的路径，或直接修改此常量。
export const MODEL_PATH = "/models/sample.glb";

/**
 * 初始化 Three.js 渲染器，返回控制 API。
 */
export function initViewer(containerId = "viewer", hooks = {}) {
  const container = document.getElementById(containerId);
  if (!container) {
    throw new Error(`未找到 viewer 容器：${containerId}`);
  }

  const { onLoading, onLoaded, onError, initialModelPath = MODEL_PATH } = hooks;

  // 场景与渲染器
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf6f8fc);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  // 相机与控制器
  const camera = new THREE.PerspectiveCamera(
    60,
    container.clientWidth / container.clientHeight,
    0.1,
    100
  );
  camera.position.set(0.8, 0.6, 1.4);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enablePan = true;
  controls.minDistance = 0.2;
  controls.maxDistance = 6;
  controls.target.set(0, 0.15, 0);

  // 灯光：环境光 + 方向光（开启阴影）
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x9ca3af, 0.9);
  scene.add(hemiLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
  dirLight.position.set(2, 3, 2);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(2048, 2048);
  dirLight.shadow.camera.near = 0.1;
  dirLight.shadow.camera.far = 10;
  scene.add(dirLight);

  // 接受阴影的地面
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(6, 6),
    new THREE.ShadowMaterial({ opacity: 0.18 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.12;
  ground.receiveShadow = true;
  scene.add(ground);

  const loader = new GLTFLoader();
  let currentModel = null;
  let lastModelPath = initialModelPath;

  function disposeCurrentModel() {
    if (!currentModel) return;
    scene.remove(currentModel);
    currentModel.traverse((child) => {
      if (child.isMesh) {
        child.geometry?.dispose();
        if (Array.isArray(child.material)) {
          child.material.forEach((mat) => mat?.dispose());
        } else {
          child.material?.dispose();
        }
      }
    });
    currentModel = null;
  }

  function fitCameraToObject(object) {
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    // 模型直径的 1.8 倍作为视距，保持安全边距
    const maxDim = Math.max(size.x, size.y, size.z);
    const fitDistance =
      (maxDim / (2 * Math.tan((Math.PI * camera.fov) / 360))) * 1.8;

    controls.target.copy(center);
    camera.position.copy(
      center.clone().add(new THREE.Vector3(fitDistance, fitDistance * 0.4, fitDistance))
    );
    camera.near = fitDistance / 50;
    camera.far = fitDistance * 50;
    camera.updateProjectionMatrix();
    controls.update();
  }

  function handleGltfLoaded(gltf, revokeUrl) {
    disposeCurrentModel();

    const model = gltf.scene;
    model.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        child.material.side = THREE.FrontSide;
      }
    });

    currentModel = model;
    scene.add(model);
    fitCameraToObject(model);
    onLoaded?.();
    if (revokeUrl) URL.revokeObjectURL(revokeUrl);
  }

  function loadModel(path = lastModelPath || initialModelPath) {
    const targetPath = path || initialModelPath;
    lastModelPath = targetPath;
    onLoading?.();
    loader.load(
      targetPath,
      (gltf) => handleGltfLoaded(gltf),
      undefined,
      (err) => {
        console.error("模型加载失败", err);
        onError?.("模型加载失败，请检查文件路径或模型格式。");
      }
    );
  }

  function loadLocalFile(file) {
    if (!file) return;
    const objectUrl = URL.createObjectURL(file);
    onLoading?.();
    loader.load(
      objectUrl,
      (gltf) => handleGltfLoaded(gltf, objectUrl),
      undefined,
      (err) => {
        console.error("本地模型加载失败", err);
        URL.revokeObjectURL(objectUrl);
        onError?.("本地模型加载失败，请确认文件为有效的 GLB/GLTF。");
      }
    );
  }

  function resize() {
    const width = container.clientWidth;
    const height = container.clientHeight;
    if (width === 0 || height === 0) return;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  // 将视角重置到初始化朝向（用于“重置视角”按钮）
  function resetView() {
    controls.reset();
    controls.target.set(0, 0.15, 0);
    camera.position.set(0.8, 0.6, 1.4);
    camera.updateProjectionMatrix();
  }

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }

  loadModel(initialModelPath);
  animate();

  return {
    resize,
    resetView,
    loadModel,
    loadLocalFile,
    dispose: () => {
      renderer.dispose();
    },
  };
}
