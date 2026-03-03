# 芯片样片问题定位系统

基于 Skills 架构的智能芯片故障分析系统。

## 安装

```bash
pip install -r requirements.txt
```

## 配置

设置环境变量：

```bash
export ANTHROPIC_AUTH_TOKEN="your-api-key"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

或修改 `config.yaml` 中的配置。

## 使用

```bash
python -m cli.main analyze logs/sample.log
```
