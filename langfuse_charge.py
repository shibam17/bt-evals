import json
import urllib.request

from langfuse import get_client, Evaluation
from langfuse.experiment import LocalExperimentItem

AGENT_URL = "http://ecommerce-agent.34.177.114.165.nip.io/chat"

langfuse = get_client()

dataset = [
    LocalExperimentItem(
        input="When am I charged for my order?",
        expected_output="You are charged when the order ships.",
    )
]


def task(item):
    req = urllib.request.Request(
        AGENT_URL,
        data=json.dumps({"message": item["input"]}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["response"]


def ships_scorer(*, input, output, expected_output, metadata, **kwargs):
    text = output.lower()
    if "ship" in text and "at purchase" not in text:
        return Evaluation(name="ships_scorer", value=1.0)
    return Evaluation(name="ships_scorer", value=0.0)


result = langfuse.run_experiment(
    name="ecommerce-charge-regression",
    data=dataset,
    task=task,
    evaluators=[ships_scorer],
)

print(result.format())
