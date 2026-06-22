import os
from datetime import date
from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6J1a0m4-i8wAII5X_yol1O3m8epsOATGa4w_gR3Jn0Rgw"),
    max_tokens=2048,
    max_rpm=4,
)

digest_file = f"digest_{date.today().strftime('%Y-%m-%d')}.md"
file_tool = FileReadTool(file_path=digest_file)

# ── AGENTS ──────────────────────────────────────────────────────────────────

picker = Agent(
    role="Content Strategist",
    goal="Pick the best insight from the research digest that will resonate with AI/ML developers on Bluesky",
    backstory=(
        "You are content strategist for Deflated AI Studio — "
        "an indie AI studio building LLMs and datasets from scratch. "
        "You know what makes developers stop scrolling: "
        "surprising facts, contrarian takes, or insights others miss. "
        "Pick 1 topic from the digest that is specific and threadable."
    ),
    llm=llm,
    tools=[file_tool],
    verbose=True,
)

writer = Agent(
    role="Twitter Thread Writer",
    goal="Write an engaging, informative, authentic thread from the perspective of an indie AI builder",
    backstory=(
        f"You write Bluesky/Twitter threads for Deflated AI Studio — an indie AI studio building LLMs "
        f"and datasets from scratch. It's {date.today().year}. "
        "Write in English. Voice: casual, honest, build-in-public. Like Andrej Karpathy but more raw. "
        "No marketing speak. Acknowledge real constraints (free compute, solo builder, small scale). "
        "Be specific — real numbers, real tradeoffs, real insights. Not hype. "
        "Bluesky handle: @deflatedxyz.bsky.social — use this in the last tweet CTA. "
        "STRICT: No markdown **bold** or *italic*. Plain text only. "
        "STRICT: Each tweet must be under 300 characters."
    ),
    llm=llm,
    verbose=True,
)

editor = Agent(
    role="Social Media Editor",
    goal="Polish the thread for maximum engagement — strong hook, smooth flow, clear call to action",
    backstory=(
        "You edit Bluesky threads obsessively. You know if tweet 1 fails to grab attention, the thread dies. "
        "Check every tweet is under 300 characters and has consistent numbering (1/n format). "
        "The thread must close with a natural CTA — not forced. "
        "STRICT: Remove all markdown formatting (**bold**, *italic*) — plain text only. "
        "STRICT: Full English. No Indonesian."
    ),
    llm=llm,
    verbose=True,
)

# ── TASKS ────────────────────────────────────────────────────────────────────

pick_task = Task(
    description=(
        f"Read the file '{digest_file}' and pick 1 topic/paper that would make the best Bluesky thread. "
        "Criteria: surprising finding, contrarian angle, or actionable insight for ML developers. "
        "Explain why this topic and what the thread angle will be."
    ),
    expected_output="1 selected topic + reason + thread angle",
    agent=picker,
)

write_task = Task(
    description=(
        "Write a Bluesky thread (8-12 posts) based on the selected topic. "
        "Format each post exactly as: 1/n post text\n\n"
        "Rules:\n"
        "- Post 1: hook that stops the scroll — specific, not vague\n"
        "- Post 2-3: context / what problem exists\n"
        "- Post 4-8: main insights, one per post\n"
        "- Post 9-11: so what? what can builders do with this\n"
        "- Last post: natural CTA mentioning @deflatedxyz.bsky.social\n\n"
        "Voice: casual English, build in public, solo indie builder perspective. "
        "No markdown. Plain text only. Each post under 300 chars."
    ),
    expected_output="Complete thread 8-12 posts, numbered 1/n format, plain text, ready to post",
    agent=writer,
    context=[pick_task],
)

edit_task = Task(
    description=(
        "Review and polish the thread from Writer:\n"
        "1. Post 1 must be a strong hook — rewrite if weak\n"
        "2. Every post must be under 300 characters\n"
        "3. Numbering must be consistent: 1/n, 2/n, etc\n"
        "4. Flow between posts must be smooth\n"
        "5. Last post CTA must feel natural\n"
        "6. No markdown formatting at all — plain text only\n\n"
        "Return the final polished thread, ready to post."
    ),
    expected_output="Final polished thread, numbered 1/n format, plain text, under 300 chars each",
    agent=editor,
    context=[write_task],
)

# ── CREW ─────────────────────────────────────────────────────────────────────

crew = Crew(
    agents=[picker, writer, editor],
    tasks=[pick_task, write_task, edit_task],
    verbose=True,
)

result = crew.kickoff()

print("\n" + "="*60)
print("DEFLATED X THREAD — SIAP POST")
print("="*60)
print(result)

filename = f"thread_{date.today().strftime('%Y-%m-%d')}.md"
with open(filename, "w") as f:
    f.write(str(result))
print(f"\n✓ Disimpan ke {filename}")
