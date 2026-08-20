import argparse
import json
import os
from pathlib import Path

from crewai import Agent, Task, Crew, LLM

# crewai's prompt-cache breakpoint marker isn't stripped for litellm-routed
# providers (only the native Anthropic adapter strips it), so Mistral's API
# rejects the extra "cache_breakpoint" field with a 400. Mistral has no
# prompt-caching feature to lose here, so disable the marker entirely.
import crewai.llms.cache as _crewai_cache

_crewai_cache.mark_cache_breakpoint = lambda message: dict(message)

if "MISTRAL_API_KEY" not in os.environ:
    raise SystemExit("MISTRAL_API_KEY not set in environment")

llm = LLM(
    model="mistral/mistral-small-latest",
    api_key=os.environ["MISTRAL_API_KEY"],
    max_tokens=2048,
)

POSTS_FILE = Path(__file__).parent / "data" / "posts.json"
POSTED_FILE = Path(__file__).parent / "data" / "posted_slugs.json"


def load_posts():
    with open(POSTS_FILE) as f:
        return json.load(f)


def load_posted_slugs():
    if not POSTED_FILE.exists():
        return set()
    with open(POSTED_FILE) as f:
        return set(json.load(f))


def pick_post(slug=None):
    posts = load_posts()
    if slug:
        for p in posts:
            if p["slug"] == slug:
                return p
        raise SystemExit(f"no post with slug '{slug}' found in {POSTS_FILE}")

    posted = load_posted_slugs()
    for p in posts:  # posts.json is newest-first, matches getAllPosts() sort order
        if p["slug"] not in posted:
            return p
    raise SystemExit("every post already has a thread — pass --slug to redo one on purpose")


# ── AGENTS ──────────────────────────────────────────────────────────────────

picker = Agent(
    role="Content Strategist",
    goal="Pick the single most threadable angle from a blog post that will resonate with AI/ML developers on Bluesky",
    backstory=(
        "You are content strategist for Deflated AI Studio — "
        "an indie AI studio building LLMs and datasets from scratch. "
        "You're given one blog post that's already written. Your job isn't to summarize "
        "the whole thing — it's to find the ONE angle inside it (a surprising number, "
        "a mistake and the fix, a contrarian insight) that makes people stop scrolling."
    ),
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Bluesky Thread Writer",
    goal="Write an engaging, informative, authentic thread from the perspective of an indie AI builder",
    backstory=(
        "You write Bluesky threads for Deflated AI Studio — an indie AI studio building LLMs "
        "and datasets from scratch. Voice: casual, honest, build-in-public. Like Andrej Karpathy "
        "but more raw. No marketing speak. Acknowledge real constraints (free compute, solo "
        "builder, small scale). Be specific — real numbers, real tradeoffs, real insights. Not hype. "
        "Bluesky handle: @deflatedxyz.bsky.social — use this in the last post's CTA. "
        "STRICT: No markdown **bold** or *italic*. Plain text only. "
        "STRICT: Each post must be under 300 characters."
    ),
    llm=llm,
    verbose=True,
)

editor = Agent(
    role="Social Media Editor",
    goal="Polish the thread for maximum engagement — strong hook, smooth flow, clear call to action",
    backstory=(
        "You edit Bluesky threads obsessively. You know if post 1 fails to grab attention, the thread dies. "
        "Check every post is under 300 characters and has consistent numbering (e.g. 1/10, 2/10 — the real total, never a literal 'n'). "
        "The thread must close with a natural CTA — not forced. "
        "STRICT: Remove all markdown formatting (**bold**, *italic*) — plain text only. "
        "STRICT: Full English. No Indonesian."
    ),
    llm=llm,
    verbose=True,
)


def build_crew(post):
    source_text = "\n\n".join(post["paragraphs"])

    pick_task = Task(
        description=(
            f"Here is a blog post titled '{post['title']}':\n\n{source_text}\n\n"
            "Pick the single best angle for a Bluesky thread. "
            "Criteria: surprising finding, contrarian angle, or actionable insight for ML developers. "
            "Explain why this angle and what the thread's arc will be."
        ),
        expected_output="1 selected angle + reason + thread arc",
        agent=picker,
    )

    write_task = Task(
        description=(
            "Write a Bluesky thread (8-12 posts) based on the selected angle. "
            "Format each post exactly as: 1/TOTAL post text — e.g. 1/10, 2/10 (TOTAL is the real post count, never write the literal letter n)\n\n"
            "Rules:\n"
            "- Post 1: hook that stops the scroll — specific, not vague\n"
            "- Post 2-3: context / what problem exists\n"
            "- Post 4-8: main insights, one per post\n"
            "- Post 9-11: so what? what can builders do with this\n"
            "- Last post: natural CTA mentioning @deflatedxyz.bsky.social\n\n"
            "Voice: casual English, build in public, solo indie builder perspective. "
            "No markdown. Plain text only. Each post under 300 chars."
        ),
        expected_output="Complete thread 8-12 posts, numbered with real counts like 1/10, plain text, ready to post",
        agent=writer,
        context=[pick_task],
    )

    edit_task = Task(
        description=(
            "Review and polish the thread from Writer:\n"
            "1. Post 1 must be a strong hook — rewrite if weak\n"
            "2. Every post must be under 300 characters\n"
            "3. Numbering must be consistent real counts, e.g. 1/10, 2/10, etc — never a literal 'n'\n"
            "4. Flow between posts must be smooth\n"
            "5. Last post CTA must feel natural\n"
            "6. No markdown formatting at all — plain text only\n\n"
            "Return the final polished thread, ready to post."
        ),
        expected_output="Final polished thread, numbered with real counts like 1/10, plain text, under 300 chars each",
        agent=editor,
        context=[write_task],
    )

    return Crew(agents=[picker, writer, editor], tasks=[pick_task, write_task, edit_task], verbose=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default=None, help="which blog post to use (default: oldest not-yet-threaded)")
    args = ap.parse_args()

    post = pick_post(args.slug)
    print(f"→ using post: {post['slug']} ({post['title']})")

    crew = build_crew(post)
    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("DEFLATED BLUESKY THREAD — READY")
    print("=" * 60)
    print(result)

    Path("drafts").mkdir(exist_ok=True)
    filename = f"drafts/thread_{post['slug']}.md"
    with open(filename, "w") as f:
        f.write(str(result))
    print(f"\n✓ Saved to {filename}")
    print(f"  source post: {post['slug']}")


if __name__ == "__main__":
    main()
