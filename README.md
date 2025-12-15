# 运营商后端服务 API

## 🚀 项目概述
在线运营商服务后端API，基于 Django + Django REST Framework。

## ✨ 功能特性
- ✅ 用户认证系统 (JWT)
- ✅ 客户管理
- ✅ 服务产品管理
- ✅ 计费订阅系统
- ✅ 工单客服系统
- ✅ 数据报表统计

## 🛠 技术栈
- **后端框架**: Django 4.2 + Django REST Framework
- **数据库**: PostgreSQL
- **认证**: JWT (djangorestframework-simplejwt)
- **API文档**: drf-spectacular (OpenAPI 3.0)
- **部署**: Docker + Nginx + Gunicorn

## 📦 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 13+
- Redis (可选)

### 安装步骤
```bash
# 克隆项目
git clone https://github.com/YOUR-USERNAME/operator-backend-api.git
cd operator-backend-api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库等

# 数据库迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 运行开发服务器
python manage.py runserver