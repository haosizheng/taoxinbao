---
domain: nlp
tags:
- Streamlit
- LLM
- Legal-Aid
- AI-Agent
datasets:
models:
- iic/qwen-max
- iic/qwen-vl-plus
license: Apache License 2.0
---

# 🛡️ 薪盾 - 讨薪宝 (Salary Shield)

> **让每一位劳动者都有底气。**  
> 薪盾是一款专为劳动者设计的移动端 AI 维权工具。通过大模型技术，我们为用户提供从证据整理、告知书生成到谈判建议的全链路法律辅助支持。

## ✨ 核心特性

- **📱 移动优先 UI**：基于 Streamlit 打造的精美移动端界面，采用扁平化设计与 iOS 风格交互。
- **📝 智能维权建档**：三步完成案卷初始化，快速锁定关键法律要素。
- **💬 AI 对抗话术**：内置“老张”话术助手。支持语音输入，AI 自动拆解老板拖延套路，生成强力回击逻辑。
- **📷 证据智能提取**：集成 Qwen-VL 视觉能力。上传聊天截图或工资单，AI 自动提取欠款金额、日期等要素并自动填充。
- **📄 法律文书生成**：一键生成专业的“正式告知书”，并支持导出为标准 PDF 文件。
- **⚖️ 24 小时律师顾问**：基于 Qwen-Max 的法律事实摘要生成，辅助整理案情。
- **📍 维权地图**：内置属地化维权机构信息与一键拨打 12348 官方热线。

## 🛠️ 技术架构

- **前端框架**：Streamlit (极速 Web 应用框架)
- **UI 组件**：Streamlit Antd Components / Streamlit Extras
- **AI 引擎**：
  - **推理层**：ModelScope (阿里巴巴通义千问 Qwen 系列)
  - **视觉识别**：Qwen-VL
  - **语音识别 (ASR)**：Alibaba Cloud ASR SDK
- **后端逻辑**：Python + FPDF (文档自动化生成)

## 🚀 快速开始

### 1. 本地部署

```bash
# 1. 克隆项目
git clone https://www.modelscope.cn/studios/gousonglin22/test-001.git
cd test-001

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
streamlit run app.py
```

### 2. 配置说明

在应用进入“个人中心”后，配置您的 **API 密钥 (Token)** 即可启用全部 AI 功能。

---

## ⚖️ 免责声明

本应用由 AI 驱动，生成的内容仅供参考，不构成正式法律意见。如遇复杂纠纷，请务必咨询专业律师或政府维权渠道。