# WalnutTwin · Step1 Web 3D Viewer

以 Three.js + Vite 搭建的数字核桃 3D 展示原型，目标是**在网页上加载并可交互查看一个 GLTF/GLB 模型**，并带有参数侧栏和基础灯光/阴影支持。

---

## 开发者准则（先读）
- **技术栈**：Vite（Vanilla JS）、Three.js、GLTF/GLB 模型文件。
- **Node 版本**：建议 >= 18（推荐 20 LTS），使用 npm/yarn/pnpm 均可，以下示例使用 npm。
- **代码风格**：模块化、少量注释解释关键设计；UI/样式用原子化 CSS 变量方便调整；中文注释补充关键三维参数。
- **资源管理**：所有本地模型放在 `public/models/`；默认提供占位模型，可替换为自有模型并保持路径。
- **开发节奏**：先保证渲染管线正确（相机、光源、controls），再做 UI 与数据 mock，最后再考虑性能与模型替换。

---

## 运行步骤
```bash
npm install
npm run dev
# 浏览器打开 http://localhost:5173
```

### 替换模型
- 将你的模型文件放到 `public/models/`，然后在 `src/viewer.js` 的 `MODEL_PATH` 指向新文件即可（建议使用 GLB 单文件）。
- 或在界面右侧点击「选择本地 GLB / GLTF」或直接拖拽文件到左侧视图区域，加载本地文件（仅浏览器本地，不会上传）。

---

## 项目结构
```
WalnutTwin/
├─ public/
│  └─ models/
│     └─ sample.glb         # 占位模型（可替换）
├─ src/
│  ├─ viewer.js             # Three.js 渲染核心
│  ├─ ui.js                 # 参数侧栏渲染
│  └─ main.js               # 应用入口
├─ docs/
│  └─ DEV_GUIDE.md          # 技术指引与开发注意事项
└─ index.html               # 页面结构
```

---

## 开发计划（当前阶段）
1) **初始化工程与依赖**：Vite + Three.js，提供占位模型与基础样式。
2) **三维渲染管线**：场景/相机/光源/阴影、OrbitControls、模型加载与尺寸自适配。
3) **UI 与交互**：参数侧栏（mock 数据）、重置视角按钮、加载状态/错误提示。
4) **调试与扩展**：简单的环境检查、下一步指引（模型替换/后端对接）。

---

## 完成标准（Step1）
- 开发服务器可启动，页面可访问。
- 默认模型成功加载，可旋转/缩放/平移（OrbitControls）。
- 场景具备基础光源与阴影效果。
- 右侧参数栏展示 mock 数据。
- README 说明完整，可根据说明替换模型并继续迭代。

---

## 参考
- Three.js 文档：https://threejs.org/docs/
- GLTF 规范：https://www.khronos.org/gltf/
- 开源模型示例库：https://github.com/KhronosGroup/glTF-Sample-Models
