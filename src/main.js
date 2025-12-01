import "./style.css";
import { initViewer } from "./viewer.js";
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

function bootstrap() {
  if (!ensureWebGLSupport()) {
    showError("当前浏览器不支持 WebGL，请使用现代浏览器或开启硬件加速。");
    return;
  }

  renderParameters(mockParameters);
  setLoading(true);

  const viewer = initViewer("viewer", {
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
