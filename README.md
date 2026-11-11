# Yihan Zhang — Portfolio

个人作品集网站，包含主页、四个 Project、个人经历与 Contact。使用 HTML、CSS、JavaScript，可以直接部署，无需安装依赖或执行构建。

## 直接连接 GitHub 部署

仓库地址：<https://github.com/willowzhangyihan001-del/yihan-portpolio>

在 Vercel 或 Netlify 中导入此仓库，选择 `main` 分支，项目根目录保持为仓库根目录。仓库自带两个平台的配置文件，发布入口 `index.html` 已放在根目录。

| 设置 | Vercel | Netlify |
| --- | --- | --- |
| 项目根目录 / Base directory | 仓库根目录 | 仓库根目录 |
| 框架 | Other | 静态网站，无需框架 |
| 构建命令 | 留空 | 留空 |
| 输出目录 / Publish directory | `.` | `.` |

如果之前的项目设置里填写了 `portfolio`、`portfolio/dist` 或 `dist`，请改回仓库根目录，然后部署最新的 `main` 提交。新导入项目时无需添加这些路径。

## 仓库结构

```text
index.html                  首页
project-1.html              KARIOS
project-2.html              Token Office
project-3.html              Constellia
project-4.html              Neckotics
resume.html                 简历预览
assets/                     图片、字体及字体授权
*.css / *.js                页面样式与交互
vercel.json                 Vercel 静态发布配置
netlify.toml                Netlify 静态发布配置
.gitignore                  本地工作文件排除规则
```

本机的旧 `portfolio/` 与 `reference-analysis/` 目录作为工作备份保留，不再上传到 GitHub。修改正式网站时，请编辑仓库根目录的网页、样式、脚本和 `assets/`。

## 本地预览

在仓库根目录执行：

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

打开 <http://127.0.0.1:8765/>。主页中进入 Project，再点击 Home，会直接回到原来的项目卡片区，不重新加载主页。点击浏览器刷新后会回到页首，并重置入场动画。

## 部署检查

依次检查根网址、`/project-1.html` 和 `/assets/contact-yihan.png`，再打开四个 Project，确认手绘导航和 Home 返回操作正常。

四个 Project 都是实际存在的 `.html` 页面。请保留 `.html` 地址，不要添加把所有请求重写到主页的 SPA 通配规则，以免项目预览加载成主页。

平台说明：[Vercel](https://vercel.com/docs/builds/configure-a-build)、[Netlify](https://docs.netlify.com/build/configure-builds/overview/)。
