# README_step2 · 视频/稀疏帧到网页的自动重建流

目标：用户只需“录一圈视频”，后端用稀疏采样帧 +（可选）ARKit 位姿/内参完成 MVS 重建，导出 GLB + 点云，并生成可在浏览器直接打开的静态网页。Step1 的 Three.js Viewer 继续沿用，支持 `?model=` 查询指定模型路径。

## 目录与新增组件
```
WalnutTwin/
├─ reconstruction/
│  ├─ reconstruct.py          # 视频/照片 -> COLMAP MVS -> Open3D 网格 -> GLB -> 可选网页打包
│  ├─ extract_frames.py       # 从视频抽帧（可单独使用，默认 2 fps + 2K 尺寸）
│  ├─ create_page.py          # 将 dist 打包成可分享的静态页并写入 GLB
│  ├─ requirements.txt        # Python 依赖（open3d 等）
│  ├─ sample_input/           # 示例输入（留空）
│  └─ outputs/                # 运行输出（database.db / sparse / dense / meshes / web）
├─ src/                       # Three.js Viewer（支持 `?model=` 参数）
├─ public/models/             # 可直接放生成的 GLB（例如 generated.glb）
└─ dist/                      # `npm run build` 产物，供打包网页使用
```

## 环境要求
- COLMAP 本地可执行（`colmap -h` 能跑）。Windows 建议用官方 prebuilt zip。
- ffmpeg 可用（视频抽帧）。
- Python 3.10+：`pip install -r reconstruction/requirements.txt`
- Node 18+：`npm install`；打包网页需 `npm run build`

## 快速上手：视频 → 稀疏帧 → GLB → 网页
```bash
# 0) 如果需要网页包，先构建前端
npm run build

# 1) 准备输入
#    - 视频：放入 reconstruction/sample_input/run.mov
#    - 或已有照片：放入 reconstruction/sample_input/

# 2) 运行重建（视频示例；会自动抽帧）
python reconstruction/reconstruct.py \
  --video reconstruction/sample_input/run.mov \
  --fps 2 --max-size 2048 \
  --workspace reconstruction/outputs/demo \
  --glb-name walnut.glb \
  --export-public \                         # 复制 GLB 到 public/models/generated.glb
  --page-output reconstruction/outputs/demo/web  # 将 dist + GLB 打成可分享网页

# 3) 预览
#    - 查看 Step1：npm run dev（或 npm run preview）后访问
#      http://localhost:5173/?model=/models/generated.glb
#    - 查看打包页：cd reconstruction/outputs/demo/web && python -m http.server 8000
#      打开 http://localhost:8000/index.html?model=./models/walnut.glb
```

## 脚本说明
- `reconstruct.py`
  - 输入：`--video`（自动抽帧）或 `--images`（已有照片）。`--fps` 控制抽帧速率，`--max-size` 控制长边。
  - 核心参数：`--workspace`、`--colmap-bin`、`--poisson-depth`、`--target-triangles`、`--reuse`、`--export-public`、`--page-output`、`--glb-name`。
  - 输出：`workspace/sparse`、`workspace/dense/fused.ply`、`workspace/meshes/<glb-name>`。`--export-public` 会复制到 `public/models/generated.glb`。`--page-output` 调用 `create_page.py` 打包 dist + GLB。
- `extract_frames.py`
  - 独立抽帧：`python reconstruction/extract_frames.py --video input.mov --output reconstruction/outputs/frames --fps 2 --max-size 2048`
- `create_page.py`
  - 独立打包：`python reconstruction/create_page.py --glb <path-to-glb> --output <target-dir> --dist dist --model-name my.glb`

## 扫描/采集侧引导（关键约束）
- 核桃固定、背景简单；光线适中，避免强反光；iPhone 围绕一圈，保持匀速（环形进度条可提示覆盖度）。
- 端侧抽帧：每 3–5 帧或位移/旋转超阈值采关键帧；仅在 tracking 正常时采样，过快移动提示“放慢”。
- 分辨率控制：长边 ≤ 2K，关键帧 60–120 张；若有 LiDAR 深度可存同名 PNG 并在后续 MVS 融合（后端扩展接口预留）。

## 策略与排错
- COLMAP 失败：检查路径是否含中文/空格，确认 ffmpeg 抽帧输出存在；可先 `--reuse` 跳过已完成的 dense。
- 模型过重：调低 `--target-triangles`（如 30000）或降低抽帧 fps / 分辨率。
- 查看模型：`?model=` 支持相对/绝对路径；GLTF 需携带资源文件并放同级。

## 完成标准（Step2）
- 视频或照片输入可跑通，生成 `dense/fused.ply`。
- Open3D 导出 GLB，Step1 Viewer 通过 `?model=` 正常加载与重置视角。
- 能输出包含 dist + GLB 的静态网页文件夹，http server 打开即能查看模型；同时保留点云用于后续分析。
