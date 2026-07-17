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
<img width="1190" height="1684" alt="image" src="https://github.com/user-attachments/assets/3c0b59a6-b251-4ad4-a762-8fb2e59c32f0" />

# 讨薪宝

> **委屈变证据，讨薪有底气**  
> 讨薪宝是一款专为劳动者设计的移动端维权工具。通过大模型技术，我们期望为用户提供从讨薪话术、证据整理、告知书生成到维权支持的服务。
> 这个项目最初是参与黑客松社会创新赛道的项目，遗憾取得第四名，无缘奖项，但我并不服气。项目的灵感来源自本人母亲真实的讨薪经历和维权困境，面对老板的一百种拖延归还欠款的理由，普通劳动人们往往是无奈的，他们既没有社会地位而又善良——这是一件天大的坏事。所以就有了这款概念产品。

## 核心功能

- **AI 讨薪话术**：普通劳动者的“开口难”和老板群体的“套路多”问题。内置讨薪话术，当用户面对老板拖延和拒绝支付工资时，只需输入对方发来的聊天记录，便可获得不卑不亢、可供复制发送给老板的讨薪话术。
- **智能维权建档**：根据用户提供的事件描述，以及文本、图片、语音资料生成一份维权卷宗，供后续介入法律维权服务时快速对齐和沟通使用。
- **法律文书生成**：一键生成“催薪告知书”，并支持导出，用户可以直接发送给讨薪对象。告知书会包含基本信息、催薪事由、法律依据、诉讼时效等必要信息。
- **维权地图**：内置当地劳动维权机构信息。
- **未来展望**：如以上方式都无法完成讨薪，期望引入专业催讨、律师、公益律师服务。

## 相关图片
<img width="3331" height="1286" alt="image" src="https://github.com/user-attachments/assets/45644189-d962-4f9c-8928-d7b38e895850" />


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
