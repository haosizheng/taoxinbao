步骤2：在本地项目中编写配置文件#
魔搭定义了一套 JSON 格式的部署配置文件ms_deploy.json，以向平台“快速创建并部署”模式提供必要的配置字段。这些字段包括但不限于：

sdk_type：部署 SDK 类型。可选值为"gradio", "streamlit", "static", "docker"之一。
sdk_version：SDK版本。当sdk_type="gradio"时，需根据json_schema中sdk_version枚举值列表，提供详细的gradio版本信息。
base_image：基础镜像版本。当sdk_type="gradio"或sdk_type="streamlit"时，需根据json_schema中base_image枚举值列表，提供详细的镜像版本信息。
resource_configuration：关联的云资源。为待部署项目配置适合的云资源，当前选择“快速创建并部署时”可选值为"platform/2v-cpu-16g-mem", "xgpu/8v-cpu-32g-mem-16g", "xgpu/8v-cpu-64g-mem-48g"之一，暂不支持选择其他个人云资源。如需选择 xgpu 资源，请先申请加入 「xGPU乐园」 组织，审批通过后才能开通 xGPU 体验资格，否则将会报错，详情可阅读 xGPU创空间介绍文档了解。
environment_variables：环境变量。项目运行期间必须依赖的环境变量，为字典类型，name为环境变量名称，value为环境变量值。
port：服务端口。当sdk_type="docker"时，必须提供port字段，当前必须填写值为7860。
详细的配置文件字段及相关说明，请通过 JSON Schema 获取，并根据schema完成配置文件编写。您可以根据相关说明手动完成编写，也可以通过将 ms_deploy.json 的 Schema 要求及相关项目文件提供给 AI 编程工具，通过 AI 辅助生成。

ms_deploy.json 示例#
一个完整、适合提交给平台部署的配置文件示例如下：

Gradio类型
{
  "sdk_type": "gradio",
  "sdk_version": "6.2.0",
  "resource_configuration": "platform/2v-cpu-16g-mem",
  "base_image": "ubuntu22.04-py311-torch2.3.1-modelscope1.31.0",
  "environment_variables": [
    {"name": "MODEL_NAME", "value": "my-model"},
    {"name": "API_KEY", "value": "sk-xxxxxx"}
  ]
}
Docker类型
{
	"$schema": "https://modelscope.cn/api/v1/studios/deploy_schema.json",
	"sdk_type": "docker",
	"resource_configuration": "platform/2v-cpu-16g-mem",
	"port": 7860,
    "environment_variables": [
        {"name": "MODEL_NAME", "value": "my-model"},
        {"name": "API_KEY", "value": "sk-xxxxxx"}
  ]
}
Static类型
{
	"$schema": "https://modelscope.cn/api/v1/studios/deploy_schema.json",
	"sdk_type": "static",
	"resource_configuration": "platform/2v-cpu-16g-mem",
}