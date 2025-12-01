import "./style.css";
import { initViewer, MODEL_PATH } from "./viewer.js";
import {
  bindResetButton,
  bindLocalFileInput,
  bindDragAndDrop,
  hideError,
  mockParameters,
  renderParameters,
  setLoading,
  showError,
} from "./ui.js";

function ensureWebGLSupport() {
  const canvas = document.createElement("canvas");
  const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
  return Boolean(gl);
}

function getInitialModelPath() {
  const params = new URLSearchParams(window.location.search);
  return params.get("model") || MODEL_PATH;
}

function bootstrap() {
  if (!ensureWebGLSupport()) {
    showError("当前浏览器不支持 WebGL，请使用现代浏览器或开启硬件加速。");
    return;
  }

  renderParameters(mockParameters);
  setLoading(true);

  const viewer = initViewer("viewer", {
    initialModelPath: getInitialModelPath(),
    onLoading: () => setLoading(true),
    onLoaded: () => {
      setLoading(false);
      hideError();
    },
    onError: (message) => {
      setLoading(false);
      showError(message);
    },
  });

  bindResetButton(() => viewer.resetView());
  bindLocalFileInput((file) => viewer.loadLocalFile(file));
  bindDragAndDrop("viewer", {
    onFile: (file) => viewer.loadLocalFile(file),
    onError: (message) => showError(message),
  });
  window.addEventListener("resize", () => viewer.resize());
}

bootstrap();
