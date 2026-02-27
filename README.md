# batch-resize-images

基于火山引擎TOS 对象存储 + Nano Banana 大模型的批量调整图片尺寸比例。

## ✨ 功能特点

-  在保持图片整体内容不变的情况下，调整图片的尺寸比例，支持:3:4、9：16等。


## 🛠️ 环境要求

- Python 3.12+
- 火山引擎账号 (需开通 TOS & 方舟 Ark/豆包服务 & 模型聚网站接口调用权限)

## 📦 安装使用步骤

第一步： **克隆项目**
   ```bash
   git clone https://github.com/yanshizhao/batch-resize-images.git

第二步：
   cd <项目文件夹>
   执行 python main.py <图片所在本地文件夹> <模型接口平台> <图片尺寸比例> 1k