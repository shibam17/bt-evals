import json
import os
import urllib.request

from braintrust import Eval, Reporter

# Real ecommerce support agent (same target used in the Harness AI Evals experiment).
# Public demo endpoint, no auth. If an auth token is ever needed, read it from
# the AGENT_API_KEY env var - never hardcode credentials.
AGENT_URL = os.environ.get("AGENT_URL", "http://ecommerce-agent.34.177.114.165.nip.io/chat")


def task(input: str) -> str:
    req = urllib.request.Request(
        AGENT_URL,
        data=json.dumps({"message": input}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["response"]


def ships_scorer(output: str, expected: str, **kwargs) -> float:
    # 1.0 if the answer says charging happens at shipment, 0.0 otherwise.
    text = output.lower()
    return 1.0 if "ship" in text and "at purchase" not in text else 0.0


def report_eval(evaluator, result, verbose, jsonl):
    passed = all(r.scores.get("ships_scorer", 0.0) >= 1.0 for r in result.results)
    for r in result.results:
        print(f"[gate] ships_scorer={r.scores.get('ships_scorer')} -> {'PASS' if r.scores.get('ships_scorer', 0.0) >= 1.0 else 'FAIL'}")
    return passed


def report_run(results, verbose, jsonl):
    success = all(results)
    print(f"[gate] run successful: {success}")
    return success


ships_gate = Reporter(
    name="ships-gate",
    report_eval=report_eval,
    report_run=report_run,
)

Eval(
    "shibamDevrel",  # project name
    data=lambda: [
        {
            "input": "When am I charged for my order?",
            "expected": "You are charged when the order ships.",
        }
    ],
    task=task,
    scores=[ships_scorer],
    reporter=ships_gate,
)
