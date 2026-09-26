import json
import asyncio
import time
import sys
import os

# Add parent directory to path to import agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import HRAgent

async def run_evaluation():
    with open("evaluation/eval_dataset.json", "r") as f:
        dataset = json.load(f)
        
    agent = HRAgent()
    await agent.connect()
    
    total = len(dataset)
    tool_success = 0
    answer_success = 0
    
    start_time = time.time()
    
    for i, item in enumerate(dataset):
        print(f"Evaluating {i+1}/{total}: {item['query']}")
        
        t0 = time.time()
        result = await agent.chat(item["query"])
        t1 = time.time()
        
        trace = result["trace"]
        response = result["response"]
        
        # Check tool use
        tools_called = [t["tool"] for t in trace]
        if item["expected_tool"] in tools_called:
            tool_success += 1
            
        # Check answer snippet
        if item["expected_answer_snippet"].lower() in response.lower():
            answer_success += 1
            
        print(f"  - Tools called: {tools_called}")
        print(f"  - Latency: {t1 - t0:.2f}s")
        
    await agent.disconnect()
    
    total_time = time.time() - start_time
    print(f"\n--- Evaluation Results ---")
    print(f"Tool Selection Accuracy: {tool_success / total * 100:.2f}%")
    print(f"Answer Accuracy (Snippet Match): {answer_success / total * 100:.2f}%")
    print(f"Average Latency: {total_time / total:.2f}s")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
