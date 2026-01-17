
亮点
我们推出了Qwen3-235B-A22B非思考模式的更新版本，命名为Qwen3-235B-A22B-Instruct-2507，具有以下关键改进：

显著提升了通用能力，包括指令执行、逻辑推理、文本理解、数学、科学、编码和工具使用。
大幅增加了多种语言的长尾知识覆盖。
在主观和开放式任务中更好地符合用户偏好，使响应更有帮助，生成的文本质量更高。
增强了对256K长上下文的理解能力。
image/jpeg

模型概述
Qwen3-235B-A22B-Instruct-2507 具有以下特点：

类型：因果语言模型
训练阶段：预训练与后训练
参数数量：总计235B，激活22B
非嵌入参数数量：234B
层数：94层
注意力头（GQA）数量：Q为64，KV为4
专家数量：128个
激活的专家数量：8个
上下文长度：原生支持262,144个token，可扩展至1,010,000个token
注意：此模型仅支持非思考模式，输出中不会生成<think></think>块。同时，不再需要指定enable_thinking=False。

有关更多详细信息，包括基准评估、硬件要求和推理性能，请参阅我们的博客、GitHub和文档。

性能
Deepseek-V3-0324	GPT-4o-0327	Claude Opus 4 非思考	Kimi K2	Qwen3-235B-A22B 非思考	Qwen3-235B-A22B-Instruct-2507
知识						
MMLU-Pro	81.2	79.8	86.6	81.1	75.2	83.0
MMLU-Redux	90.4	91.3	94.2	92.7	89.2	93.1
GPQA	68.4	66.9	74.9	75.1	62.9	77.5
SuperGPQA	57.3	51.0	56.5	57.2	48.2	62.6
SimpleQA	27.2	40.3	22.8	31.0	12.2	54.3
CSimpleQA	71.1	60.2	68.0	74.5	60.8	84.3
推理						
AIME25	46.6	26.7	33.9	49.5	24.7	70.3
HMMT25	27.5	7.9	15.9	38.8	10.0	55.4
ARC-AGI	9.0	8.8	30.3	13.3	4.3	41.8
ZebraLogic	83.4	52.6	-	89.0	37.7	95.0
LiveBench 20241125	66.9	63.7	74.6	76.4	62.5	75.4
编程						
LiveCodeBench v6 (25.02-25.05)	45.2	35.8	44.6	48.9	32.9	51.8
MultiPL-E	82.2	82.7	88.5	85.7	79.3	87.9
Aider-Polyglot	55.1	45.3	70.7	59.0	59.6	57.3
对齐						
IFEval	82.3	83.9	87.4	89.8	83.2	88.7
Arena-Hard v2*	45.6	61.9	51.5	66.1	52.0	79.2
Creative Writing v3	81.6	84.9	83.8	88.1	80.4	87.5
WritingBench	74.5	75.5	79.2	86.2	77.0	85.2
代理						
BFCL-v3	64.7	66.5	60.1	65.2	68.0	70.9
TAU1-Retail	49.6	60.3#	81.4	70.7	65.2	71.3
TAU1-Airline	32.0	42.8#	59.6	53.5	32.0	44.0
TAU2-Retail	71.1	66.7#	75.5	70.6	64.9	74.6
TAU2-Airline	36.0	42.0#	55.5	56.5	36.0	50.0
TAU2-Telecom	34.0	29.8#	45.2	65.8	24.6	32.5
多语言能力						
MultiIF	66.5	70.4	-	76.2	70.2	77.5
MMLU-ProX	75.8	76.2	-	74.5	73.2	79.4
INCLUDE	80.1	82.1	-	76.9	75.6	79.5
PolyMATH	32.2	25.5	30.0	44.8	27.0	50.2
*: 为了可重复性，我们报告了由 GPT-4.1 评估的胜率。

#: 结果是使用 GPT-4o-20241120 生成的，因为无法访问 GPT-4o-0327 的原生函数调用 API。

快速开始
Qwen3-MoE 的代码已经在最新的 Hugging Face transformers 中，建议您使用 transformers 的最新版本。

使用 transformers<4.51.0 时，您会遇到以下错误：

KeyError: 'qwen3_moe'
以下包含一个代码片段，说明如何根据给定的输入使用模型生成内容。

from modelscope import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen3-235B-A22B-Instruct-2507"

# load the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

# prepare the model input
prompt = "Give me a short introduction to large language model."
messages = [
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# conduct text completion
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=16384
)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

content = tokenizer.decode(output_ids, skip_special_tokens=True)

print("content:", content)
对于部署，您可以使用 sglang>=0.4.6.post1 或 vllm>=0.8.5 或创建一个与 OpenAI 兼容的 API 端点：

SGLang:
SGLANG_USE_MODELSCOPE=true python -m sglang.launch_server --model-path Qwen/Qwen3-235B-A22B-Instruct-2507 --tp 8 --context-length 262144
vLLM:
VLLM_USE_MODELSCOPE=true vllm serve Qwen/Qwen3-235B-A22B-Instruct-2507 --tensor-parallel-size 8 --max-model-len 262144
注意：如果您遇到内存不足（OOM）问题，请考虑将上下文长度减少到较短的值，例如 32,768。

对于本地使用，Ollama、LMStudio、MLX-LM、llama.cpp 和 KTransformers 等应用程序也支持 Qwen3。

代理使用
Qwen3 在工具调用能力方面表现出色。我们建议使用 Qwen-Agent 来充分利用 Qwen3 的代理能力。Qwen-Agent 内部封装了工具调用模板和工具调用解析器，大大降低了编码复杂性。

要定义可用的工具，您可以使用 MCP 配置文件，使用 Qwen-Agent 的集成工具，或自行集成其他工具。

from qwen_agent.agents import Assistant

# Define LLM
llm_cfg = {
    'model': 'Qwen3-235B-A22B-Instruct-2507',

    # Use a custom endpoint compatible with OpenAI API:
    'model_server': 'http://localhost:8000/v1',  # api_base
    'api_key': 'EMPTY',
}

# Define Tools
tools = [
    {'mcpServers': {  # You can specify the MCP configuration file
            'time': {
                'command': 'uvx',
                'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
            },
            "fetch": {
                "command": "uvx",
                "args": ["mcp-server-fetch"]
            }
        }
    },
  'code_interpreter',  # Built-in tools
]

# Define Agent
bot = Assistant(llm=llm_cfg, function_list=tools)

# Streaming generation
messages = [{'role': 'user', 'content': 'https://qwenlm.github.io/blog/ Introduce the latest developments of Qwen'}]
for responses in bot.run(messages=messages):
    pass
print(responses)
处理超长文本
为了支持 超长上下文处理（高达 100 万个 token），我们集成了两种关键技术：

双块注意力 (DCA)：一种长度外推方法，将长序列分割成可管理的块，同时保持全局一致性。
MInference：一种稀疏注意力机制，通过专注于关键 token 交互来减少计算开销。
这些创新共同显著提高了超过 256K token 序列的 生成质量和推理效率。在接近 1M token 的序列上，系统相比标准注意力实现可以达到 3 倍的速度提升。

有关完整的技术细节，请参阅 Qwen2.5-1M 技术报告。

如何启用 1M Token 上下文
NOTE

要有效处理 100 万个 token 的上下文，用户需要大约 1000 GB 的总 GPU 内存。这包括模型权重、KV 缓存存储和峰值激活内存需求。

步骤 1：更新配置文件
下载模型并将您的 config.json 内容替换为 config_1m.json，其中包括长度外推和稀疏注意力的配置。

export MODELNAME=Qwen3-235B-A22B-Instruct-2507
huggingface-cli download Qwen/${MODELNAME} --local-dir ${MODELNAME}
mv ${MODELNAME}/config.json ${MODELNAME}/config.json.bak
mv ${MODELNAME}/config_1m.json ${MODELNAME}/config.json
步骤 2：启动模型服务器
更新配置后，使用 vLLM 或 SGLang 来服务模型。

选项 1：使用 vLLM
要运行支持 1M 上下文的 Qwen：

pip install -U vllm \
    --torch-backend=auto \
    --extra-index-url https://wheels.vllm.ai/nightly
然后启用双块闪存注意力启动服务器：

VLLM_ATTENTION_BACKEND=DUAL_CHUNK_FLASH_ATTN VLLM_USE_V1=0 \
VLLM_USE_MODELSCOPE=true vllm serve ./Qwen3-235B-A22B-Instruct-2507 \
  --tensor-parallel-size 8 \
  --max-model-len 1010000 \
  --enable-chunked-prefill \
  --max-num-batched-tokens 131072 \
  --enforce-eager \
  --max-num-seqs 1 \
  --gpu-memory-utilization 0.85
关键参数
参数	用途
VLLM_ATTENTION_BACKEND=DUAL_CHUNK_FLASH_ATTN	启用自定义注意力内核以提高长上下文效率
--max-model-len 1010000	将最大上下文长度设置为约1M tokens
--enable-chunked-prefill	允许对非常长的输入进行分块预填充（避免内存不足）
--max-num-batched-tokens 131072	在预填充期间控制批量大小；平衡吞吐量和内存
--enforce-eager	禁用CUDA图捕获（对于双块注意力是必需的）
--max-num-seqs 1	由于极端内存使用，限制并发序列数量
--gpu-memory-utilization 0.85	设置用于模型执行器的GPU内存比例
选项2：使用SGLang
首先，克隆并安装专门的分支：

git clone https://github.com/sgl-project/sglang.git
cd sglang
pip install -e "python[all]"
使用DCA支持启动服务器：

SGLANG_USE_MODELSCOPE=true python3 -m sglang.launch_server \
    --model-path ./Qwen3-235B-A22B-Instruct-2507 \
    --context-length 1010000 \
    --mem-frac 0.75 \
    --attention-backend dual_chunk_flash_attn \
    --tp 8 \
    --chunked-prefill-size 131072
关键参数
参数	用途
--attention-backend dual_chunk_flash_attn	激活双块Flash Attention
--context-length 1010000	定义最大输入长度
--mem-frac 0.75	用于静态分配的内存比例（模型权重和KV缓存内存池）。如果遇到内存不足错误，请使用较小的值。
--tp 8	张量并行大小（与模型分片匹配）
--chunked-prefill-size 131072	处理长输入时的预填充块大小，避免内存不足
故障排除：
遇到错误：“模型的最大序列长度（xxxxx）大于KV缓存中可以存储的最大token数。”或“RuntimeError: 内存不足。请尝试增加--mem-fraction-static。”

为KV缓存预留的VRAM不足。

vLLM: 考虑减少max_model_len或增加tensor_parallel_size和gpu_memory_utilization。或者，你可以减少max_num_batched_tokens，尽管这可能会显著减慢推理速度。
SGLang: 考虑减少context-length或增加tp和mem-frac。或者，你可以减少chunked-prefill-size，尽管这可能会显著减慢推理速度。
遇到错误：“torch.OutOfMemoryError: CUDA内存不足。”

为激活权重预留的VRAM不足。你可以尝试降低gpu_memory_utilization或mem-frac，但请注意这可能会减少可用于KV缓存的VRAM。

遇到错误：“输入提示（xxxxx tokens）+ 前瞻槽位（0）过长，超出了块管理器的容量。”或“输入（xxx xtokens）比模型的上下文长度（xxx tokens）更长。”

输入太长。考虑使用较短的序列或增加max_model_len或context-length。

长上下文性能
我们在RULER基准测试的1M版本上测试了该模型。

模型名称	Acc avg	4k	8k	16k	32k	64k	96k	128k	192k	256k	384k	512k	640k	768k	896k	1000k
Qwen3-235B-A22B (非思考)	83.9	97.7	96.1	97.5	96.1	94.2	90.3	88.5	85.0	82.1	79.2	74.4	70.0	71.0	68.5	68.0
Qwen3-235B-A22B-Instruct-2507 (全注意力)	92.5	98.5	97.6	96.9	97.3	95.8	94.9	93.9	94.5	91.0	92.2	90.9	87.8	84.8	86.5	84.5
Qwen3-235B-A22B-Instruct-2507 (稀疏注意力)	91.7	98.5	97.2	97.3	97.7	96.6	94.6	92.8	94.3	90.5	89.7	89.5	86.4	83.6	84.2	82.5
所有模型均在启用双块注意力的情况下进行评估。
由于评估耗时较长，我们对每个长度使用了260个样本（13个子任务，每个子任务20个样本）。
最佳实践
为了达到最佳性能，我们建议以下设置：

采样参数：

我们建议使用 Temperature=0.7、TopP=0.8、TopK=20 和 MinP=0。
对于支持的框架，您可以在0到2之间调整 presence_penalty 参数以减少无尽重复。但是，使用较高的值可能会偶尔导致语言混合和模型性能略微下降。
充足的输出长度：对于大多数查询，我们建议使用16,384个令牌的输出长度，这对于指令模型是足够的。

标准化输出格式：在基准测试时，我们建议使用提示来标准化模型输出。

数学问题：在提示中包含“请逐步推理，并将最终答案放在 \boxed{} 中。”
选择题：在提示中添加以下JSON结构以标准化响应：“请在 answer 字段中仅显示选项字母，例如，"answer": "C"。”