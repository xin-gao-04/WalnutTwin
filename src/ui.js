const overlay = () => document.getElementById("overlay");
const errorBanner = () => document.getElementById("errorBanner");
const paramsContainer = () => document.getElementById("parameters");
const dropHint = () => document.getElementById("dropHint");

export const mockParameters = [
  { label: "长度", value: "43 mm" },
  { label: "宽度", value: "40 mm" },
  { label: "高度", value: "48 mm" },
  { label: "质量", value: "52 g" },
  { label: "表面粗糙度", value: "0.67" },
  { label: "纹理分级", value: "A级" },
];

export function renderParameters(data = mockParameters) {
  const container = paramsContainer();
  if (!container) return;
  container.innerHTML = data
    .map(
      (item) => `
      <div class="param">
        <div class="label">${item.label}</div>
        <div class="value">${item.value}</div>
      </div>
    `
    )
    .join("");
}

export function bindResetButton(handler) {
  const btn = document.getElementById("resetCamera");
  if (!btn) return;
  btn.addEventListener("click", handler);
}

export function bindLocalFileInput(handler) {
  const input = document.getElementById("localModel");
  if (!input) return;
  input.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    handler(file);
    // 重置 input 值，方便再次选择同一个文件
    e.target.value = "";
  });
}

export function setLoading(isLoading) {
  const el = overlay();
  if (!el) return;
  el.classList.toggle("hidden", !isLoading);
}

export function bindDragAndDrop(targetId, { onFile, onError } = {}) {
  const target = document.getElementById(targetId);
  const hint = dropHint();
  if (!target || !hint) return;

  const prevent = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const hideHint = () => hint.classList.add("hidden");
  const showHint = () => hint.classList.remove("hidden");

  ["dragenter", "dragover", "dragleave", "drop"].forEach((event) => {
    target.addEventListener(event, prevent);
  });

  target.addEventListener("dragenter", showHint);
  target.addEventListener("dragover", showHint);
  target.addEventListener("dragleave", hideHint);
  target.addEventListener("drop", (e) => {
    hideHint();
    const file = e.dataTransfer?.files?.[0];
    if (!file) return;
    const ext = file.name.toLowerCase();
    if (!ext.endsWith(".glb") && !ext.endsWith(".gltf")) {
      onError?.("仅支持 GLB / GLTF 文件拖拽加载。");
      return;
    }
    onFile?.(file);
  });
}

export function showError(message) {
  const el = errorBanner();
  if (!el) return;
  el.textContent = message;
  el.classList.remove("hidden");
}

export function hideError() {
  const el = errorBanner();
  if (!el) return;
  el.classList.add("hidden");
}
