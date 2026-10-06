"""GPT-6 Luna launcher: inject a model into the lab's native functions without modifying provided code."""
import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler, UsageMetadataCallbackHandler
from langchain_openai import ChatOpenAI

from lab.curator import curate_skills
from lab.runner import CONDITIONS, run_task
from lab.tasks import ROOT, list_tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["probe", "run", "curate"])
    parser.add_argument("--condition", choices=sorted(CONDITIONS), default="baseline")
    parser.add_argument("--tasks", nargs="+", default=["learn"])
    parser.add_argument("--results", default="results")
    parser.add_argument("--recursion-limit", type=int, default=60)
    parser.add_argument("--evidence", default="report/evidence")
    args = parser.parse_args()
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is missing; configure it locally without printing the key.")
    requested = os.getenv("LAB_MODEL", "openai:gpt-6-luna")
    if requested not in {"openai:gpt-6-luna", "gpt-6-luna"}:
        parser.error("This launcher is for the user-selected gpt-6-luna only.")
    model = ChatOpenAI(
        model="gpt-6-luna", use_responses_api=True, output_version="v0", reasoning={"effort": "medium"},
        temperature=None, max_tokens=8192, timeout=120, max_retries=1,
    )
    evidence = Path(args.evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    receipt = {
        "timestamp": datetime.now(timezone.utc).isoformat(), "action": args.action,
        "model": "gpt-6-luna", "api": "responses", "reasoning_effort": "medium",
        "output_version": "v0",
        "temperature": None, "max_output_tokens": 8192, "recursion_limit": args.recursion_limit,
        "python": sys.version.split()[0], "platform": platform.platform(),
        "dependencies": {p: version(p) for p in ["deepagents", "langchain-openai", "langchain-core", "openai"]},
    }
    if args.action == "probe":
        usage = UsageMetadataCallbackHandler()
        reply = model.invoke("Reply with OK only.", config={"callbacks": [usage]})
        receipt.update({"response": reply.content, "usage": usage.usage_metadata})
        print("probe: response received", flush=True)
    elif args.action == "curate":
        if list((ROOT / "skills" / "auto").glob("*/SKILL.md")):
            parser.error("Skills already exist; preserve the previous curator snapshot before rerunning.")
        # The native curator invokes the injected model; callbacks record actual generation evidence.
        class CuratorEvidence(BaseCallbackHandler):
            def on_chat_model_start(self, serialized, messages, **kwargs):
                receipt["prompt"] = [[m.content for m in batch] for batch in messages]

            def on_llm_end(self, response, **kwargs):
                receipt["response"] = response.generations[0][0].message.content

        usage = UsageMetadataCallbackHandler()
        model.callbacks = [CuratorEvidence(), usage]
        paths = curate_skills(results_dir=args.results, source_condition=args.condition, model=model)
        receipt.update({"skills": [str(p.relative_to(ROOT)) for p in paths], "usage": usage.usage_metadata})
        print("curator wrote:", ", ".join(receipt["skills"]), flush=True)
    else:
        tasks = args.tasks
        if tasks in (["learn"], ["eval"], ["all"]):
            tasks = [t.id for t in list_tasks(None if tasks == ["all"] else tasks[0])]
        if any(t.endswith("-eval") for t in tasks) and not (ROOT / "report" / "FREEZE_READY.md").exists():
            parser.error("Evaluation is gated until hypotheses and freeze are recorded in report/FREEZE_READY.md.")
        if any(t.endswith("-eval") for t in tasks):
            freeze_check = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_freeze.py")], capture_output=True, text=True)
            if freeze_check.returncode:
                parser.error("Native freeze verification failed; fix the protocol before evaluating.")
        for task in tasks:
            if (Path(args.results) / args.condition / task / "run.json").exists():
                parser.error(f"Existing results for {args.condition}/{task}; use a separate --results path.")
        summaries = []
        diagnostics = []
        current_task = None
        live_path = evidence / f"requests-{stamp}.jsonl"

        class RunDiagnostics(BaseCallbackHandler):
            def on_llm_end(self, response, **kwargs):
                message = response.generations[0][0].message
                event = {
                    "metadata": {key: value for key, value in message.response_metadata.items()
                                 if key in {"id", "model_name", "finish_reason", "status", "incomplete_details"}},
                    "usage": message.usage_metadata,
                }
                diagnostics.append(event)
                with live_path.open("a", encoding="utf-8") as log:
                    log.write(json.dumps({"task": current_task, **event}) + "\n")

        model.callbacks = [RunDiagnostics()]
        receipt["diagnostics"] = {}
        for task in tasks:
            current_task = task
            diagnostics.clear()
            record = run_task(task, args.condition, results_dir=args.results, model=model, recursion_limit=args.recursion_limit)
            receipt["diagnostics"][task] = list(diagnostics)
            summaries.append({k: record[k] for k in ["task", "score", "tokens", "seconds", "error"]})
            print(f"{args.condition} {task}: {record['passed']}/{record['total']} "
                  f"tokens={record['tokens']['total']} calls={record['tool_calls']} seconds={record['seconds']} "
                  f"error={record['error']}", flush=True)
            if record["error"]:
                break
        receipt.update({"condition": args.condition, "results_dir": args.results, "runs": summaries})
    (evidence / f"{args.action}-{stamp}.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.action == "run" and any(r["error"] for r in receipt["runs"]):
        return 1
    if args.action == "curate" and not receipt["skills"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
