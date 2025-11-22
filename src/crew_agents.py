#!/usr/bin/env python3
"""
CrewAI Agent Integration
Orchestrates VPN detection pipeline using CrewAI agents with multiple LLM options.
"""

import os
import subprocess
from typing import Type
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ============================================================================
# LLM CONFIGURATION
# ============================================================================

def get_llm():
    """
    Configure LLM based on available API keys or local setup.
    Priority: Ollama (free/local) > OpenAI > Gemini
    """
    # Option 1: Use Ollama (recommended - free and local)
    # Install: https://ollama.ai
    # Run: ollama pull llama3.2:1b
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            return "ollama/llama3.2:1b"
    except:
        pass
    
    # Option 2: OpenAI (requires API key with credits)
    if os.getenv("OPENAI_API_KEY"):
        return "gpt-4o-mini"
    
    # Option 3: Gemini (requires API key)
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini/gemini-1.5-flash"
    
    # Fallback: Provide instructions
    raise ValueError(
        "No LLM configured. Please choose one:\n"
        "1. Install Ollama (FREE): https://ollama.ai then run 'ollama pull llama3.2:1b'\n"
        "2. Set OPENAI_API_KEY environment variable\n"
        "3. Set GOOGLE_API_KEY environment variable"
    )


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

class CaptureToolInput(BaseModel):
    """Input schema for PCAP capture tool."""
    input_path: str = Field(default="data/", description="Path to PCAP files directory")


class CaptureTool(BaseTool):
    """Converts PCAP files to CSV flow records."""
    name: str = "Capture and Preprocess Flows"
    description: str = (
        "Captures network traffic from PCAP files, converts them to CSV using nfstream, "
        "and performs initial preprocessing and normalization."
    )
    args_schema: Type[BaseModel] = CaptureToolInput
    
    def _run(self, input_path: str = "data/") -> str:
        """Execute PCAP to CSV conversion and preprocessing."""
        print(f"\n[Agent 1: Flow Capture] Processing PCAPs from {input_path}...")
        
        try:
            # Step 1: PCAP to CSV
            subprocess.run("python3 src/pcap_to_csv.py", shell=True, check=True)
            
            # Step 2: Preprocess
            subprocess.run(
                "python3 src/preprocess_kaggle_traffic.py "
                "--input data/combined_flows.csv "
                "--output data/processed_flows_1.csv",
                shell=True, check=True
            )
            
            return "✓ Successfully captured and preprocessed flows. Output: data/processed_flows_1.csv"
        except subprocess.CalledProcessError as e:
            return f"✗ Error: {str(e)}"


class FlowAnalysisToolInput(BaseModel):
    """Input schema for flow analysis tool."""
    csv_path: str = Field(description="Path to CSV file containing flow data")


class FlowAnalysisTool(BaseTool):
    """Analyzes flow-level statistics and IP reputation."""
    name: str = "Analyze Flow Patterns and Reputation"
    description: str = (
        "Analyzes general flow statistics (bytes, packets, ports) and assesses "
        "IP reputation against threat intelligence databases."
    )
    args_schema: Type[BaseModel] = FlowAnalysisToolInput
    
    def _run(self, csv_path: str) -> str:
        """Execute flow pattern and reputation analysis."""
        print(f"\n[Agent 2: Flow Pattern Analyst] Analyzing {csv_path}...")
        
        try:
            # Flow analyzer
            subprocess.run(
                f"python3 src/flow_analyzer.py "
                f"--csv {csv_path} "
                f"--out-json results/flow_analyzer/summary.json",
                shell=True, check=True
            )
            
            # Reputation analysis
            subprocess.run(
                f"python3 src/reputation_analysis.py "
                f"--csv {csv_path} "
                f"--out-json results/reputation_analysis/report.json",
                shell=True, check=True
            )
            
            return (
                "✓ Flow pattern and reputation analysis complete.\n"
                "Outputs: results/flow_analyzer/summary.json, results/reputation_analysis/report.json"
            )
        except subprocess.CalledProcessError as e:
            return f"✗ Error: {str(e)}"


class TemporalAnalysisToolInput(BaseModel):
    """Input schema for temporal analysis tool."""
    csv_path: str = Field(description="Path to CSV file containing flow data")


class TemporalAnalysisTool(BaseTool):
    """Analyzes temporal patterns in network traffic."""
    name: str = "Analyze Temporal Patterns"
    description: str = (
        "Analyzes timing patterns including inter-arrival times, burst behavior, "
        "jitter, and temporal entropy to distinguish VPN traffic."
    )
    args_schema: Type[BaseModel] = TemporalAnalysisToolInput
    
    def _run(self, csv_path: str) -> str:
        """Execute temporal pattern analysis."""
        print(f"\n[Agent 3: Temporal Analyst] Analyzing timing patterns for {csv_path}...")
        
        try:
            subprocess.run(
                f"python3 src/temporal_agent.py "
                f"--csv {csv_path} "
                f"--out-dir results/temporal_agent",
                shell=True, check=True
            )
            
            return "✓ Temporal analysis complete. Output: results/temporal_agent/temporal_summary.json"
        except subprocess.CalledProcessError as e:
            return f"✗ Error: {str(e)}"


class SizeAnalysisToolInput(BaseModel):
    """Input schema for size analysis tool."""
    csv_path: str = Field(description="Path to CSV file containing flow data")


class SizeAnalysisTool(BaseTool):
    """Analyzes packet sizes and TLS fingerprints."""
    name: str = "Analyze Packet Sizes and TLS"
    description: str = (
        "Analyzes packet size distributions, traffic volume patterns, "
        "and TLS/SSL handshake fingerprints to detect encryption overhead."
    )
    args_schema: Type[BaseModel] = SizeAnalysisToolInput
    
    def _run(self, csv_path: str) -> str:
        """Execute size and TLS analysis."""
        print(f"\n[Agent 4: Size & Payload Analyst] Analyzing packet sizes and TLS for {csv_path}...")
        
        try:
            # Size distribution analysis
            subprocess.run(
                f"python3 src/size_agent.py "
                f"--csv {csv_path} "
                f"--out-dir results/size_agent",
                shell=True, check=True
            )
            
            # TLS analysis
            subprocess.run(
                f"python3 src/tls_analysis.py "
                f"--csv {csv_path} "
                f"--out-dir results/tls_analysis",
                shell=True, check=True
            )
            
            return (
                "✓ Size and TLS analysis complete.\n"
                "Outputs: results/size_agent/size_analysis.json, results/tls_analysis/tls_summary.json"
            )
        except subprocess.CalledProcessError as e:
            return f"✗ Error: {str(e)}"


class FeatureEngineeringToolInput(BaseModel):
    """Input schema for feature engineering tool."""
    csv_path: str = Field(description="Path to preprocessed CSV file")


class FeatureEngineeringTool(BaseTool):
    """Aggregates all features into ML-ready dataset."""
    name: str = "Generate ML Features"
    description: str = (
        "Aggregates analysis results from all agents (flow, temporal, size, TLS, reputation) "
        "into a comprehensive ML-ready feature dataset."
    )
    args_schema: Type[BaseModel] = FeatureEngineeringToolInput
    
    def _run(self, csv_path: str) -> str:
        """Execute feature engineering."""
        print(f"\n[Agent 5: Feature Engineer] Generating ML features from {csv_path}...")
        
        try:
            subprocess.run(
                f"python3 src/feature_engineering.py "
                f"--flows {csv_path} "
                f"--temporal results/temporal_agent/temporal_summary.json "
                f"--size results/size_agent/size_analysis.json "
                f"--tls results/tls_analysis/tls_summary.json "
                f"--reputation results/reputation_analysis/report.json "
                f"--out results/ml_ready/flows_ml_ready.csv",
                shell=True, check=True
            )
            
            return "✓ Feature engineering complete. Final dataset: results/ml_ready/flows_ml_ready.csv"
        except subprocess.CalledProcessError as e:
            return f"✗ Error: {str(e)}"


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

def create_agents(llm):
    """Create the 5 specialized agents."""
    
    # Agent 1: Network Traffic Collector
    flow_capture_agent = Agent(
        role='Network Traffic Collector',
        goal='Capture raw network packets from PCAP files and convert them into structured flow data',
        backstory=(
            'You are an expert in network packet capture and preprocessing. '
            'Your specialty is extracting clean, structured flow records from raw PCAP files '
            'using tools like nfstream. You ensure data quality and proper formatting.'
        ),
        tools=[CaptureTool()],
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 2: Traffic Pattern Analyst
    flow_pattern_agent = Agent(
        role='Traffic Pattern Analyst',
        goal='Identify macro-level traffic patterns and assess IP reputation',
        backstory=(
            'You analyze the general behavior of network flows, looking for volume anomalies, '
            'unusual port usage, and suspicious IP addresses. You cross-reference IPs against '
            'known threat intelligence databases to identify potential security risks.'
        ),
        tools=[FlowAnalysisTool()],
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 3: Temporal Behavior Analyst
    temporal_agent = Agent(
        role='Temporal Behavior Analyst',
        goal='Analyze the timing and burstiness patterns of network traffic',
        backstory=(
            'You specialize in time-series analysis of network packets. Your expertise is in '
            'detecting jitter, bursts, and inter-arrival time patterns that distinguish '
            'VPN-encrypted traffic from normal traffic. You understand how tunneling affects timing.'
        ),
        tools=[TemporalAnalysisTool()],
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 4: Payload Analyst
    size_agent = Agent(
        role='Payload Analyst',
        goal='Analyze packet sizes and TLS fingerprints',
        backstory=(
            'You examine packet size distributions and TLS handshake metadata. Your skill is in '
            'identifying encryption overhead, MTU effects, and TLS version patterns that indicate '
            'tunneling protocols. You can detect VPN signatures in packet size patterns.'
        ),
        tools=[SizeAnalysisTool()],
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    # Agent 5: Feature Engineer
    feature_engineer_agent = Agent(
        role='Feature Engineer',
        goal='Construct a comprehensive feature set for Machine Learning',
        backstory=(
            'You are a data scientist who aggregates insights from all other analysts. '
            'You create normalized, high-quality feature vectors by combining flow statistics, '
            'temporal patterns, size distributions, TLS fingerprints, and reputation scores '
            'into a unified dataset ready for ML model training.'
        ),
        tools=[FeatureEngineeringTool()],
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return [flow_capture_agent, flow_pattern_agent, temporal_agent, size_agent, feature_engineer_agent]


# ============================================================================
# TASK DEFINITIONS
# ============================================================================

def create_tasks(agents):
    """Create tasks for each agent."""
    
    flow_capture_agent, flow_pattern_agent, temporal_agent, size_agent, feature_engineer_agent = agents
    
    task_capture = Task(
        description=(
            'Process all PCAP files in the data/VPN-PCAPS-01 and data/NonVPN-PCAPs-01 directories. '
            'Convert them to CSV flow records and perform initial preprocessing. '
            'Ensure the output is clean and ready for analysis.'
        ),
        expected_output='A preprocessed CSV file at data/processed_flows_1.csv',
        agent=flow_capture_agent
    )
    
    task_pattern = Task(
        description=(
            'Analyze the flow patterns in data/processed_flows_1.csv. '
            'Extract flow statistics, identify top ports, and assess IP reputation. '
            'Look for anomalies that might indicate VPN usage.'
        ),
        expected_output='Summary JSON files for flow analysis and reputation at results/flow_analyzer/ and results/reputation_analysis/',
        agent=flow_pattern_agent,
        context=[task_capture]
    )
    
    task_temporal = Task(
        description=(
            'Perform temporal analysis on data/processed_flows_1.csv. '
            'Calculate inter-arrival times, detect bursts, measure jitter, and compute entropy. '
            'Identify timing patterns characteristic of VPN traffic.'
        ),
        expected_output='A temporal summary JSON file at results/temporal_agent/temporal_summary.json',
        agent=temporal_agent,
        context=[task_capture]
    )
    
    task_size = Task(
        description=(
            'Analyze packet size distributions and TLS fingerprints in data/processed_flows_1.csv. '
            'Look for encryption overhead, MTU patterns, and TLS version signatures. '
            'Identify characteristics of tunneled traffic.'
        ),
        expected_output='Summary JSON files for size and TLS analysis at results/size_agent/ and results/tls_analysis/',
        agent=size_agent,
        context=[task_capture]
    )
    
    task_features = Task(
        description=(
            'Aggregate all analysis results into a final ML-ready feature dataset. '
            'Combine flow statistics, temporal patterns, size distributions, TLS fingerprints, '
            'and reputation scores. Normalize and prepare for model training.'
        ),
        expected_output='A final CSV file ready for ML training at results/ml_ready/flows_ml_ready.csv',
        agent=feature_engineer_agent,
        context=[task_pattern, task_temporal, task_size]
    )
    
    return [task_capture, task_pattern, task_temporal, task_size, task_features]


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute the VPN detection crew."""
    
    print("="*80)
    print("VPN DETECTION CREW - AI-POWERED MULTI-AGENT ANALYSIS")
    print("="*80)
    
    # Get LLM configuration
    try:
        llm = get_llm()
        print(f"\n✓ LLM configured: {llm}\n")
    except ValueError as e:
        print(f"\n✗ {str(e)}\n")
        return
    
    # Create agents and tasks
    agents = create_agents(llm)
    tasks = create_tasks(agents)
    
    # Create and run crew
    vpn_detection_crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential  # Execute tasks in order
    )
    
    print("\n" + "="*80)
    print("Starting Crew Execution...")
    print("="*80 + "\n")
    
    try:
        result = vpn_detection_crew.kickoff()
        
        print("\n" + "="*80)
        print("✓ CREW EXECUTION COMPLETE")
        print("="*80)
        print(f"\nFinal Output:\n{result}")
        
        print("\n" + "="*80)
        print("Next Steps:")
        print("="*80)
        print("1. Review results in results/ml_ready/flows_ml_ready.csv")
        print("2. Train ML models: python src/train_vpn_classifier.py --data results/ml_ready/flows_ml_ready.csv")
        
    except Exception as e:
        print(f"\n✗ Crew execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
