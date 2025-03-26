# 新闻关键词舆情监控系统 - 新手使用指南

本指南专为没有编程经验的新闻专业人士设计，帮助您使用GitHub Codespaces轻松运行新闻关键词舆情监控系统。

## 第一部分：准备工作

### 1. 登录GitHub账号
- 访问 https://github.com/login
- 输入您的用户名和密码登录

## 第二部分：创建仓库并上传代码

### 1. 创建新仓库
- 访问 https://github.com/new
- 在"Repository name"中输入：`news-monitor-system`
- 选择"Public"（公开）
- 勾选"Add a README file"
- 点击绿色的"Create repository"按钮

### 2. 上传代码文件
- 在新创建的仓库页面，点击"Add file" > "Upload files"
- 将我之前发给您的压缩包解压后的所有文件拖拽到上传区域
- 在页面底部填写描述（可选）："上传新闻监控系统代码"
- 点击绿色的"Commit changes"按钮

## 第三部分：启动Codespaces

### 1. 创建Codespace
- 在仓库主页，点击绿色的"Code"按钮
- 选择"Codespaces"标签
- 点击"Create codespace on main"
- 等待几分钟，系统会自动设置开发环境

### 2. 运行系统
- 当Codespaces加载完成后，您会看到一个类似VS Code的界面
- 在底部找到终端（Terminal）窗口，如果没有打开，可以点击顶部菜单的Terminal > New Terminal
- 在终端中输入以下命令并按Enter：
  ```
  pip install -r requirements.txt
  ```
- 等待安装完成后，输入以下命令并按Enter：
  ```
  python app.py
  ```
- 系统启动后，会显示一个链接，通常是形如"https://xxxx-xxxx.preview.app.github.dev"的地址
- 点击该链接或按住Ctrl键点击（Mac用户按Command键点击）

## 第四部分：使用系统

### 1. 添加关键词
- 在系统界面中，点击导航栏中的"关键词管理"
- 在表单中输入您感兴趣的关键词（如"人工智能"）和分类（如"科技"）
- 点击"添加"按钮

### 2. 添加平台
- 点击导航栏中的"平台管理"
- 添加您想监控的平台，如：
  - 名称：腾讯新闻，类型：tencent
  - 名称：今日头条，类型：toutiao
  - 名称：微信公众号，类型：weixin
  - 名称：微博，类型：weibo

### 3. 抓取新闻
- 点击导航栏中的"新闻抓取"
- 选择您添加的关键词
- 选择要抓取的平台
- 设置每个平台抓取的数量
- 点击"开始抓取"按钮

### 4. 查看分析结果
- 点击导航栏中的"舆情分析"
- 选择关键词和时间范围
- 点击"分析"按钮
- 查看趋势图、情感分析、平台分布等数据

## 第五部分：保存您的工作

Codespaces会自动保存您的数据，但为了安全起见：

- 您可以在终端中输入`Ctrl+C`停止系统
- 关闭Codespace时，它会自动保存状态
- 下次使用时，只需在GitHub仓库页面点击"Code" > "Codespaces"，选择已有的Codespace即可继续使用

## 常见问题解答

### Q: 系统运行时出现错误怎么办？
A: 尝试在终端中输入`pip install --upgrade pip`更新pip，然后重新安装依赖。

### Q: 如何关闭系统？
A: 在运行系统的终端中按`Ctrl+C`。

### Q: 如何重新启动系统？
A: 在终端中输入`python app.py`。

### Q: 数据会丢失吗？
A: Codespaces会保存您的数据，但建议定期导出重要数据。

### Q: 如何获取更多帮助？
A: 可以参考系统中的README.md文件，或者联系系统管理员。
