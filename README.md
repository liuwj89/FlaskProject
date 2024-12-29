# 基于Flask的学生选课管理系统

这是一个使用 Flask 框架和 Layui web组件库设计的学生选课管理系统。

## 项目结构

- `app/`: 包含 Flask 应用的主要代码
- `templates/`: 包含 HTML 模板文件
- `static/`: 包含静态文件（如 CSS、JavaScript、图片等）
- `requirements.txt`: 列出项目依赖的 Python 包

## 安装

1. 克隆仓库到本地：
    ```bash
    git clone https://github.com/lumos706/FlaskProject.git
    ```

2. 进入项目目录：
    ```bash
    cd FlaskProject
    ```

3. 创建虚拟环境并激活：
    ```bash
    python -m venv venv
    source venv/bin/activate  # 对于 Windows 系统使用 `venv\Scripts\activate`
    ```
    当然，你也可以使用自己的python环境

4. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
    

## 运行

激活虚拟环境后，运行以下命令以创建本地数据库（PostgreSQL）。请确保您的设备上安装了PostgreSQL。

```bash
python create.py

```

随后启动 Flask 应用：

```bash
python app.py
```

应用将运行在 http://127.0.0.1:5000/ 。
