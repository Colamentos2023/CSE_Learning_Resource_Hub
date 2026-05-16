# Control Nexus / 智控学园

A Learning Resource Hub for Control Engineering.

本仓库是控制科学与工程相关课程的静态课程资源库与学业导航平台，使用 Astro Starlight 构建，并通过 GitHub Actions 部署到 GitHub Pages。

## 本地开发

```bash
npm install
npm run generate
npm run dev
```

## 构建

```bash
npm run build
```

## 部署

仓库已配置 `.github/workflows/deploy.yml`。推送到 `main` 后，GitHub Actions 会执行：

```bash
npm ci
npm run build
```

并将 `dist/` 发布到 GitHub Pages。Astro 已配置：

- `site`: `https://colamentos2023.github.io`
- `base`: `/CSE_Learning_Resource_Hub/`

## 目录结构

```text
src/content/docs/                 # Starlight 文档页面
src/content/docs/resources/        # 学习资料与课程页面
src/content/docs/experiences/      # 学习经验与其他经验页面
src/content/docs/contribute/       # 资料贡献说明
public/resources/                  # 可预览/下载的公开资源附件
reports/                           # 大文件与隐私审核报告
scripts/generate_site.py           # 资料扫描、分类、页面生成脚本
```

## 资料贡献方式

1. 将原始资料放入本地 `控制分享资料` 目录。
2. 运行 `npm run generate` 重新扫描、分类、复制资源并生成页面。
3. 检查 `reports/sensitive-review-needed.md` 与 `reports/large-files-report.md`。
4. 运行 `npm run build` 确认站点可以构建。
5. 提交并推送更改。

新增同一课程下不同同学资料时，请在文件名中保留来源、作者、年份或简短描述，避免覆盖。上传前必须检查姓名、学号、手机号、邮箱、群号、二维码、教师个人联系方式等敏感信息。
