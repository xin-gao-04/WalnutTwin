# WalnutTwin · 开发者技术指引

## 环境
- Node >= 18（推荐 20 LTS）
- npm / yarn / pnpm 均可，示例使用 npm。
- 本地目录结构保持 Vite 默认：
  - `public/models/` 放置 GLB/GLTF 模型（默认 `sample.glb`）。
  - `src/viewer.js` 定义模型默认路径 `MODEL_PATH`。

## 常用命令
```bash
npm install        # 安装依赖
npm run dev        # 本地开发，http://localhost:5173
npm run build      # 生产构建
npm run preview    # 预览生产包
```

## 功能点速览
- Three.js 渲染管线：场景、相机、OrbitControls、半球光+方向光、阴影、地面接收阴影。
- 模型加载：默认加载 `MODEL_PATH`；支持侧栏按钮选择本地 GLB/GLTF（浏览器内存储，对外不上传）。
- 视图控制：旋转/缩放/平移；重置视角按钮调用 `resetView()`。
- UI：参数 mock 数据展示、加载遮罩、错误提示。

## 开发建议
1. **替换模型**：将文件放入 `public/models/` 并更新 `MODEL_PATH`；或通过界面按钮加载本地 GLB 进行快速验证。
2. **控制相机**：修改 `controls.target` 与 `camera.position` 可以调整默认视角；`fitCameraToObject` 通过包围盒自动适配。
3. **性能调优**：若模型过大，可尝试压缩（draco/meshopt）或在 `loadModel` 中使用对应解码器；必要时做懒加载或分包。
4. **UI 扩展**：`ui.js` 的 `renderParameters` 接受数组，后端接入后直接替换数据来源即可。
5. **错误排查**：加载失败通常与路径或格式有关；控制台会输出 GLTFLoader 错误细节，前端会显示错误横幅。

## 后续迭代建议
- 接入后端模型 URL，加入下拉/列表选择。
- 加入环境贴图与 PBR 参数调节以提升材质效果。
- 增加测量/标注工具，用于交互式展示几何特征。
- 为 Three.js 依赖配置按需分包，减少初次加载体积。
