"""
Small localhost web UI for the specialist swarm.

Starts a swarm run in a background thread, streams its events to the browser
via Server-Sent Events, and lists downloadable files from outputs/.

It reuses constants and helpers from run_onboarding.py, so when you adapt that
file for Card C (new inputs, new message) the UI follows automatically.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python app.py            # then open http://127.0.0.1:5000
"""

import json
import os
import threading
import time
from pathlib import Path

from anthropic import Anthropic
from flask import Flask, Response, jsonify, send_from_directory

import run_onboarding as rd

app = Flask(__name__)

STATE = {"running": False, "events": [], "session_id": None}
LOCK = threading.Lock()


def emit(kind: str, text: str) -> None:
    with LOCK:
        STATE["events"].append({"kind": kind, "text": text})


def run_swarm() -> None:
    try:
        coordinator_id = Path(".coordinator_id").read_text().strip()
        environment_id = Path(".environment_id").read_text().strip()
        client = Anthropic()

        emit("info", "Loading input documents...")
        context = rd.load_inputs_as_context()

        session = client.beta.sessions.create(
            agent=coordinator_id,
            environment_id=environment_id,
            title="Hire-to-Onboard (web UI)",
        )
        STATE["session_id"] = session.id
        Path(".last_session_id").write_text(session.id)
        emit("info", f"Session {session.id} started")

        with client.beta.sessions.events.stream(session.id) as stream:
            client.beta.sessions.events.send(
                session.id,
                events=[
                    {
                        "type": "user.message",
                        "content": [
                            {"type": "text", "text": rd.build_user_message(context)}
                        ],
                    }
                ],
            )
            for event in stream:
                t = event.type
                if t == "session.thread_created":
                    emit("thread", f"thread spawned: {event.agent_name}")
                elif t == "session.thread_status_running":
                    emit("thread", f"thread running: {getattr(event, 'agent_name', '?')}")
                elif t == "agent.thread_message_sent":
                    emit("delegate", f"delegate to {event.to_agent_name}")
                elif t == "agent.thread_message_received":
                    emit("reply", f"reply from {event.from_agent_name}")
                elif t == "agent.tool_use":
                    emit("tool", f"tool: {getattr(event, 'name', '?')}")
                elif t == "agent.message":
                    for block in event.content:
                        if getattr(block, "type", None) == "text":
                            emit("text", block.text)
                elif t == "session.status_idle":
                    break

        rd.OUTPUT_DIR.mkdir(exist_ok=True)
        files = client.beta.files.list(
            scope_id=session.id, betas=["managed-agents-2026-04-01"]
        )
        for f in files.data:
            client.beta.files.download(f.id).write_to_file(
                str(rd.OUTPUT_DIR / f.filename)
            )
            emit("file", f.filename)
        emit("done", "Swarm finished")
    except Exception as exc:  # surface any failure in the UI
        emit("error", f"{type(exc).__name__}: {exc}")
    finally:
        STATE["running"] = False


@app.get("/")
def index() -> str:
    return PAGE


@app.post("/run")
def run():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify(error="ANTHROPIC_API_KEY not set in the server shell"), 400
    for needed in (".coordinator_id", ".environment_id"):
        if not Path(needed).exists():
            return jsonify(error=f"Missing {needed}. Run the setup scripts first."), 400
    with LOCK:
        if STATE["running"]:
            return jsonify(error="A run is already in progress"), 409
        STATE.update(running=True, events=[], session_id=None)
    threading.Thread(target=run_swarm, daemon=True).start()
    return jsonify(ok=True)


@app.get("/events")
def events():
    def gen():
        sent = 0
        while True:
            with LOCK:
                batch = STATE["events"][sent:]
                running = STATE["running"]
            for ev in batch:
                yield f"data: {json.dumps(ev)}\n\n"
            sent += len(batch)
            if not running and not batch:
                yield "event: end\ndata: {}\n\n"
                return
            time.sleep(0.3)

    return Response(gen(), mimetype="text/event-stream")


@app.get("/files")
def files():
    d = rd.OUTPUT_DIR
    names = sorted(p.name for p in d.iterdir() if p.is_file()) if d.exists() else []
    return jsonify(names)


@app.get("/outputs/<path:name>")
def download(name: str):
    return send_from_directory(rd.OUTPUT_DIR.resolve(), name, as_attachment=True)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Specialist Swarm</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--bd:#ddd;--ac:#1d4ed8;--pn:#f6f7f9}
@media(prefers-color-scheme:dark){:root{--bg:#111;--fg:#eee;--mut:#999;--bd:#333;--ac:#6ea0ff;--pn:#1a1a1a}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px}
h1{font-size:22px;margin:0 0 4px}p.sub{color:var(--mut);margin:0 0 16px}
button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:10px 18px;font-size:15px;cursor:pointer}
button:disabled{opacity:.5;cursor:not-allowed}
#log{background:var(--pn);border:1px solid var(--bd);border-radius:6px;margin-top:16px;padding:12px;
height:420px;overflow:auto;font:13px/1.5 ui-monospace,monospace;white-space:pre-wrap}
.thread{color:var(--ac)}.delegate{color:#b45309}.reply{color:#15803d}.error{color:#dc2626}.info,.tool{color:var(--mut)}
h2{font-size:16px;margin:20px 0 6px}ul{padding-left:20px}a{color:var(--ac)}
</style></head><body><main>
<h1>Specialist Swarm</h1>
<p class="sub">Run the coordinator and specialists, watch the live event stream, download the output.</p>
<button id="go">Run swarm</button>
<div id="log" aria-live="polite"></div>
<h2>Output files</h2><ul id="files"><li>none yet</li></ul>
<script>
const log=document.getElementById('log'),btn=document.getElementById('go');
function add(ev){const d=document.createElement('div');d.className=ev.kind;
d.textContent=(ev.kind==='text'?'':'['+ev.kind+'] ')+ev.text;log.appendChild(d);log.scrollTop=log.scrollHeight}
async function loadFiles(){const n=await (await fetch('/files')).json();const ul=document.getElementById('files');
ul.innerHTML=n.length?'':'<li>none yet</li>';n.forEach(f=>{const li=document.createElement('li'),a=document.createElement('a');
a.href='/outputs/'+encodeURIComponent(f);a.textContent=f;li.appendChild(a);ul.appendChild(li)})}
btn.onclick=async()=>{log.textContent='';btn.disabled=true;
const r=await fetch('/run',{method:'POST'});
if(!r.ok){add({kind:'error',text:(await r.json()).error});btn.disabled=false;return}
const es=new EventSource('/events');
es.onmessage=e=>add(JSON.parse(e.data));
es.addEventListener('end',()=>{es.close();btn.disabled=false;loadFiles()});
es.onerror=()=>{es.close();btn.disabled=false}};
loadFiles();
</script></main></body></html>
"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)
