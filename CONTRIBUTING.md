# 资料维护说明

这份文档面向仓库维护者，用来记录资料添加、分类、隐私检查和大文件处理规则。公开网站中的“资料贡献”页面只保留读者需要看到的简短入口。

## 常用命令

```bash
npm install
npm run generate
npm run build
```

## 目录规范

生成脚本会从仓库同级的 `控制分享资料/` 目录递归扫描资料，并复制可公开资源到：

```text
public/resources/courses/<course-slug>/<type-slug>/<filename>
public/resources/experiences/learning/<topic-slug>/<filename>
public/resources/experiences/other/<topic-slug>/<filename>
```

站点页面位于：

```text
src/content/docs/resources/
src/content/docs/experiences/
src/content/docs/contribute/
src/content/docs/about/
```

`src/content/docs/internal/resource-inventory.md` 是内部资料清单，默认不放入公开导航。

## 课程资料类型

课程页统一使用以下模块名：

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

## 新增资料流程

1. 将原始资料放入同级 `控制分享资料/` 目录。
2. 运行 `npm run generate` 重新扫描、分类、复制资源并生成页面。
3. 检查 `reports/sensitive-review-needed.md` 和 `reports/large-files-report.md`。
4. 检查生成页面是否有不适合公开的信息。
5. 运行 `npm run build`。
6. 提交并推送。

## 命名建议

同一课程下不同同学整理的资料不要互相覆盖。推荐文件名保留课程、类型、来源或年份等信息：

```text
<course-or-topic>-<type>-<source-or-year>.<ext>
```

如果作者、来源或年份不确定，不要猜测。

## 隐私检查

上传前检查姓名、学号、手机号、邮箱、班级群号、二维码、教师个人联系方式等敏感信息。含个人隐私、未授权传播、明显侵权或不适合公开的资料不要上传。

PDF 内容如果无法自动提取，需人工抽查。图片内容目前不做 OCR，需要人工确认。

## 大文件规则

- 普通 GitHub 仓库不要提交超过 50 MiB 的文件。
- 绝对不要提交超过 100 MiB 的文件。
- 大文件不要依赖 Git LFS 作为 GitHub Pages 直接预览资源。

如果文件过大，记录到 `reports/large-files-report.md`，建议压缩 PDF、拆分 PDF、放入 GitHub Release，或放入外部网盘后在网站中提供链接。
