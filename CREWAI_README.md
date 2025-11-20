# CrewAI Integration

This project includes **two execution modes**:

## 1. Direct Execution (Simple & Fast)
```bash
python run_pipeline.py
```
- No LLM or API keys required
- Direct execution of all steps
- Recommended for production

## 2. CrewAI Multi-Agent (AI-Powered)
```bash
python src/crew_agents.py
```
- AI agents orchestrate the pipeline
- Intelligent decision-making
- Natural language task descriptions

### LLM Configuration Options

The CrewAI integration supports multiple LLMs (in order of priority):

#### Option 1: Ollama (Recommended - FREE & Local)
```bash
# Install Ollama from https://ollama.ai
brew install ollama  # macOS
# or download from website for other OS

# Pull a model
ollama pull llama2

# Run the crew
python src/crew_agents.py
```

#### Option 2: OpenAI
```bash
export OPENAI_API_KEY="your-key-here"
python src/crew_agents.py
```

#### Option 3: Google Gemini
```bash
export GOOGLE_API_KEY="your-key-here"
python src/crew_agents.py
```

## The 5 Agents

1. **Network Traffic Collector** - Captures and preprocesses PCAP files
2. **Traffic Pattern Analyst** - Analyzes flow statistics and IP reputation
3. **Temporal Behavior Analyst** - Detects timing patterns and bursts
4. **Payload Analyst** - Analyzes packet sizes and TLS fingerprints
5. **Feature Engineer** - Aggregates all features for ML

## Benefits of CrewAI Integration

- 🤖 **Intelligent Orchestration**: AI agents make decisions based on data
- 📊 **Adaptive Analysis**: Agents can adjust their approach based on findings
- 🔄 **Self-Correcting**: Agents can retry failed steps
- 📝 **Detailed Logging**: Natural language descriptions of each step
- 🎯 **Task-Focused**: Each agent specializes in one aspect

## When to Use Each Mode

**Use Direct Execution** (`run_pipeline.py`) when:
- You want predictable, fast execution
- Running in production environments
- No LLM access or API credits

**Use CrewAI** (`crew_agents.py`) when:
- You want AI-powered orchestration
- Exploring data with intelligent analysis
- You have Ollama installed or API keys
