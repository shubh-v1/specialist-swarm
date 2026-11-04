"""
Run the Hire-to-Onboard swarm (Card C) against the synthetic new-hire profile.

Inlines the new-hire profile + supporting policy/roster/content docs into the
user message (simpler than Files API for hackathon-scale content). Streams
events as they come in so you can watch the fan-out — this is the demo,
narrate it live:
  wave 1: Recruiter, IT Provisioning and Buddy Match spawn in parallel
  wave 2: Welcome Packet spawns once Buddy Match has named the buddy

Saves the coordinator transcript and the day-1 readiness pack to outputs/.

Usage:
    python run_onboarding.py

The synthetic data is anchored to 2026-11-04 (lead times and reference
deadlines are computed from "today"). Override with ONBOARDING_AS_OF=YYYY-MM-DD.
"""

import os
from pathlib import Path

from anthropic import Anthropic


PROFILE_PATH = Path("synthetic-data/new-hire-profile.md")
SUPPORTING_FILES = [
    Path("synthetic-data/offer-policy.md"),      # Recruiter
    Path("synthetic-data/it-standards.md"),      # IT Provisioning
    Path("synthetic-data/team-roster.json"),     # Buddy Match
    Path("synthetic-data/welcome-content.md"),   # Welcome Packet
]
AS_OF = os.environ.get("ONBOARDING_AS_OF", "2026-11-04")
OUTPUT_DIR = Path("outputs")


def load_inputs_as_context() -> str:
    blocks = []
    for path in [PROFILE_PATH, *SUPPORTING_FILES]:
        if not path.exists():
            print(f"  WARNING: {path} missing — skipping")
            continue
        print(f"  including {path.name}")
        blocks.append(f"=====  DOCUMENT: {path.name}  =====\n{path.read_text()}")
    return "\n\n".join(blocks)


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    if not Path(".coordinator_id").exists() or not Path(".environment_id").exists():
        raise SystemExit(
            "Missing .coordinator_id or .environment_id. Run "
            "setup_environment.py, create_specialists.py, create_coordinator.py, "
            "then upload_skills.py first."
        )

    coordinator_id = Path(".coordinator_id").read_text().strip()
    environment_id = Path(".environment_id").read_text().strip()

    client = Anthropic()

    print("Loading new-hire profile + supporting docs...")
    context = load_inputs_as_context()

    print(f"\nStarting session against coordinator {coordinator_id}...")
    session = client.beta.sessions.create(
        agent=coordinator_id,
        environment_id=environment_id,
        title="Hire-to-Onboard — Lena Okafor (start 2026-11-30)",
    )
    Path(".last_session_id").write_text(session.id)

    user_message = (
        f"Today's date is {AS_OF}. A new hire's profile has just come through "
        "from HR. Please run the standard Hire-to-Onboard process:\n"
        "1. Read the new-hire profile yourself.\n"
        "2. Wave 1: delegate to Recruiter, IT Provisioning and Buddy Match in "
        "parallel, each with only the documents it needs and today's date.\n"
        "3. Wave 2: once Buddy Match has named the buddy, delegate to Welcome "
        "Packet (no offer terms or reference details in its brief).\n"
        "4. Reconcile the replies: dates, conditional-start implications for "
        "IT, and the buddy name must all line up.\n"
        "5. Produce the day-1 readiness pack as a branded Word document named "
        "day1-readiness-pack.docx using the docx skill. If no docx skill is "
        "available, output the pack as a structured markdown document.\n\n"
        "Specialists have their own skills attached for their respective "
        "domains. The start date is close, so flag anything with a deadline "
        "in the next few days at the top.\n\n"
        f"{context}"
    )

    # Stream the events — this is the demo. Watch for the two delegation waves.
    print("\n=== EVENT STREAM (this is the demo) ===\n")
    final_text_parts: list[str] = []

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": user_message}],
                }
            ],
        )
        for event in stream:
            t = event.type
            if t == "session.thread_created":
                print(f"  [thread spawned]   {event.agent_name}", flush=True)
            elif t == "session.thread_status_running":
                name = getattr(event, "agent_name", "?")
                print(f"  [thread running]   {name}", flush=True)
            elif t == "agent.thread_message_received":
                print(f"  [reply ←]          {event.from_agent_name}", flush=True)
            elif t == "agent.thread_message_sent":
                print(f"  [delegate →]       {event.to_agent_name}", flush=True)
            elif t == "agent.message":
                for block in event.content:
                    if getattr(block, "type", None) == "text":
                        final_text_parts.append(block.text)
                        print(block.text, end="", flush=True)
            elif t == "agent.tool_use":
                print(f"\n  [tool: {getattr(event, 'name', '?')}]", flush=True)
            elif t == "session.status_idle":
                print("\n\n[swarm finished]")
                break

    OUTPUT_DIR.mkdir(exist_ok=True)
    transcript_path = OUTPUT_DIR / "coordinator-transcript.txt"
    transcript_path.write_text("".join(final_text_parts))
    print(f"\nCoordinator transcript saved to {transcript_path}")

    # Pull every file the agents produced in the container
    print("\nDownloading deliverables from the session container...")
    files = client.beta.files.list(
        scope_id=session.id,
        betas=["managed-agents-2026-04-01"],
    )
    file_count = 0
    for f in files.data:
        out_path = OUTPUT_DIR / f.filename
        print(f"  {f.filename}  ->  {out_path}")
        content = client.beta.files.download(f.id)
        content.write_to_file(str(out_path))
        file_count += 1

    if file_count == 0:
        print("  (no files found — agents may have produced text-only output)")
    else:
        print(f"\nDownloaded {file_count} file(s) to {OUTPUT_DIR}/")
        if not (OUTPUT_DIR / "day1-readiness-pack.docx").exists():
            print("  NOTE: day1-readiness-pack.docx not among them — check the "
                  "transcript for the file name the coordinator used.")

    print(f"\nView the full session (including all sub-agent threads) at:")
    print(f"  https://platform.claude.com/sessions/{session.id}")


if __name__ == "__main__":
    main()
