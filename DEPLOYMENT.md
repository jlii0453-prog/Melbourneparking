# GitHub Pages 部署配置指南

## 项目结构说明

本项目包含两个主要HTML文件：
- `homepage.html` - 现代化的入口页面（推荐作为GitHub Pages的默认页面）
- `index.html` - 主要的数据可视化应用页面

## 方法1：重命名文件（推荐）

为了让 `homepage.html` 成为GitHub Pages的默认入口页面，最简单的方法是重命名：

1. 将 `homepage.html` 重命名为 `index.html`
2. 将原来的 `index.html` 重命名为 `app.html` 或 `dashboard.html`
3. 更新 `homepage.html` 中的链接，指向新的文件名

```bash
# 重命名文件
git mv index.html app.html
git mv homepage.html index.html
```

然后更新 `index.html`（原homepage.html）中的链接：
```html
<a href="app.html" class="start-button">Start Exploring</a>
```

## 方法2：使用GitHub Pages配置

如果您想保持文件名不变，可以通过GitHub Pages配置：

1. 在项目根目录创建 `.github/workflows/deploy.yml` 文件
2. 配置GitHub Actions来自动部署

## 方法3：使用JavaScript重定向

在 `homepage.html` 中添加自动重定向逻辑：

```javascript
// 如果直接访问homepage.html，自动重定向到index.html
if (window.location.pathname.includes('homepage.html')) {
    window.location.href = 'index.html';
}
```

## 推荐的部署流程

1. **重命名文件**（推荐使用方法1）
2. 提交更改到GitHub
3. 在GitHub仓库设置中启用GitHub Pages
4. 选择部署分支（通常是 `main` 或 `master`）
5. 等待部署完成

## 文件结构建议

```
Melbourneparking/
├── index.html          # 入口页面（原homepage.html）
├── app.html            # 主应用页面（原index.html）
├── GeoHeatmap.js       # 地图功能
├── ColorScaleLegend.js # 图例功能
├── *.css               # 样式文件
├── *.json              # 数据文件
└── *.py                # Python脚本
```

## 注意事项

- GitHub Pages 默认会查找 `index.html` 作为入口页面
- 确保所有相对路径的链接都正确更新
- 测试所有功能在重命名后是否正常工作
- 考虑添加404页面来改善用户体验

## 测试部署

部署完成后，访问您的GitHub Pages URL，应该会看到新的现代化入口页面，点击"Start Exploring"按钮后会跳转到主应用页面。
