---
title: 资料贡献说明
description: 如何为 Control Nexus 添加课程、资料与经验页面。
---

# 资料贡献说明

欢迎继续补充课程资料、学习经验和其他学业信息。提交前请先确认资料适合公开，并尽量保持目录结构稳定。

## 目录规范

推荐结构：

```text
public/resources/courses/<course-slug>/<type-slug>/<filename>
public/resources/experiences/learning/<topic-slug>/<filename>
public/resources/experiences/other/<topic-slug>/<filename>
src/content/docs/resources/courses/<course-slug>/index.md
```

页面内容放在 `src/content/docs/`，可下载或预览的附件放在 `public/resources/`。slug 使用小写英文、数字和连字符，避免中文路径影响部署。

## 资料类型

课程内部统一使用以下模块名称：

- 课程导读
- 课堂笔记
- 复习提纲
- 半开卷 A4
- 历年资料
- 回忆卷
- 实验资料
- 作业与习题
- 代码与仿真
- 其他资料

没有资料的模块不要显示为空模块。

## 新增课程流程

1. 在 `public/resources/courses/<course-slug>/` 下建立课程资料文件夹。
2. 按资料类型建立 `<type-slug>` 子目录。
3. 在 `src/content/docs/resources/courses/<course-slug>/index.md` 新建课程页面。
4. 在课程索引页和 `src/generated/sidebar.mjs` 中加入入口。
5. 如首页需要突出展示该课程，再更新首页卡片或说明。

## 命名建议

同一课程下不同同学整理的资料不要互相覆盖。推荐：

```text
<course-slug>-<type-slug>-<author-or-source>-<term-or-year>.<ext>
```

如果作者、来源或年份不确定，请不要猜测，可使用简短描述加哈希或序号。

## 推荐格式

- PDF：适合预览和下载，优先压缩到合理大小。
- Markdown / TXT：优先整理成站内页面。
- Word / PPT：能稳定转换时转为 Markdown；不能稳定转换时作为附件。
- 图片：确认不包含二维码、群号、个人联系方式等敏感内容。

## 隐私检查

上传前检查姓名、学号、手机号、邮箱、班级群号、二维码、教师个人联系方式等敏感信息。含个人隐私、未授权传播、明显侵权或不适合公开的资料不要上传。

## 大文件规则

- 检查所有 PDF 等文件大小。
- 普通 GitHub 仓库不要提交超过 50 MiB 的文件。
- 绝对不要提交超过 100 MiB 的文件。
- 大文件不要依赖 Git LFS 作为 GitHub Pages 直接预览资源。

如果文件过大，请生成 `reports/large-files-report.md`，列出文件名、大小和建议处理方式，例如压缩 PDF、拆分 PDF、放入 GitHub Release，或放入外部网盘后在网站中提供链接。

## 本地维护命令

```bash
npm run generate
npm install
npm run build
```
