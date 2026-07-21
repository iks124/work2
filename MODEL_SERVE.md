# Qwen3.5-9B vLLM 服务说明

## 当前服务

- checkpoint：`/data/GoEMem/Qwen3.5-9B`
- vLLM：`0.23.0`
- OpenAI 兼容模型名：`Qwen3.5-9B`
- 最大上下文长度：`32768`
- 权重类型：`bfloat16`
- GPU 显存利用率上限：`0.85`
- 启动日期：`2026-07-17`
- 未配置 API Key，仅应在受信任网络中开放

| GPU | 监听地址 | API Base URL | 主进程 PID | 日志 |
| --- | --- | --- | ---: | --- |
| 5 | `0.0.0.0:8002` | `http://<server-ip>:8002/v1` | `715974` | `logs/qwen3.5-9b-gpu5.log` |
| 6 | `0.0.0.0:8003` | `http://<server-ip>:8003/v1` | `716257` | `logs/qwen3.5-9b-gpu6.log` |

两个端口是独立副本，可由调用方轮询，或在前面配置负载均衡。

## 调用示例

```bash
curl http://127.0.0.1:8002/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "Qwen3.5-9B",
    "messages": [{"role": "user", "content": "用三句话介绍杭州。"}],
    "temperature": 0.6,
    "top_p": 0.9,
    "max_tokens": 512,
    "stream": false
  }'
```

将端口换成 `8003` 即调用 GPU 6 上的副本。模型可能先生成思考内容，不要把 `max_tokens` 设得过小。

## 运维命令

检查服务：

```bash
curl http://127.0.0.1:8002/v1/models
curl http://127.0.0.1:8003/v1/models
```

查看日志：

```bash
tail -f logs/qwen3.5-9b-gpu5.log
tail -f logs/qwen3.5-9b-gpu6.log
```

停止服务：

```bash
kill 715974 716257
```

PID 在重启后会变化，停止前可重新确认：

```bash
ps -ef | grep '[v]llm.*serve.*/data/GoEMem/Qwen3.5-9B'
```

## 当前启动参数

启动时需将虚拟环境的 `bin` 加入 `PATH`，供 FlashInfer JIT 调用 `ninja`。

GPU 5：

```bash
PATH=/data/GoEMem/vllm/bin:$PATH CUDA_VISIBLE_DEVICES=5 \
  /data/GoEMem/vllm/bin/python -u -m vllm.entrypoints.cli.main serve \
  /data/GoEMem/Qwen3.5-9B \
  --served-model-name Qwen3.5-9B \
  --max-model-len 32768 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.85 \
  --trust-remote-code \
  --host 0.0.0.0 \
  --port 8002
```

GPU 6：

```bash
PATH=/data/GoEMem/vllm/bin:$PATH CUDA_VISIBLE_DEVICES=6 \
  /data/GoEMem/vllm/bin/python -u -m vllm.entrypoints.cli.main serve \
  /data/GoEMem/Qwen3.5-9B \
  --served-model-name Qwen3.5-9B \
  --max-model-len 32768 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.85 \
  --trust-remote-code \
  --host 0.0.0.0 \
  --port 8003
```
