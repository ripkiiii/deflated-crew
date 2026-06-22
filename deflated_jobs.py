import os
from datetime import date
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

os.environ["SERPER_API_KEY"] = os.environ.get("SERPER_API_KEY", "1c7234686d677b501f58d6c7a555da8d5b471004")

llm = LLM(
    model="groq/llama3-8b-8192",
    api_key=os.environ.get("GROQ_API_KEY", "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"),
    max_tokens=1024,
)

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# ── AGENTS ──────────────────────────────────────────────────────────────────

scout = Agent(
    role="Internship Scout",
    goal="Temukan ML/AI internship dan research opportunities yang open sekarang",
    backstory=(
        "Kamu nyari internship untuk seorang Indonesian ML engineer/student. "
        "Target: ML Intern, AI Research Intern, SWE Intern (AI team), NLP Intern. "
        "Prioritas: remote-friendly atau international, tahun 2026, bisa apply dari Indonesia. "
        "Search di company career pages, LinkedIn, Greenhouse, Lever, HuggingFace jobs. "
        "Company target: Cohere, HuggingFace, Mistral, EleutherAI, AI2, NVIDIA, Google DeepMind, "
        "Anthropic, OpenAI, Stability AI, dan startups AI lainnya."
    ),
    llm=llm,
    tools=[search_tool],
    verbose=True,
)

filter_agent = Agent(
    role="Opportunity Filter",
    goal="Filter dan rank internship yang paling relevan dan realistis untuk diapply",
    backstory=(
        "Kamu filter internship untuk Indonesian ML student dengan profile: "
        "- Skill: Python, PyTorch, LLM training dari scratch, fine-tuning (QLoRA), NLP "
        "- Projects: IDK-1 (Indo LLM 100M), Nala (AI dokumen pemerintah), NanoPR (tiny GPT) "
        "- Status: student, bisa remote, belum lulus "
        "Filter kriteria: "
        "1. Remote atau open untuk international applicants "
        "2. ML/AI focused (bukan pure SWE tanpa AI) "
        "3. Student eligible "
        "4. Deadline belum lewat "
        "Buang yang: US citizen only, sudah expired, atau butuh degree yang belum dimiliki."
    ),
    llm=llm,
    tools=[scrape_tool],
    verbose=True,
)

summarizer = Agent(
    role="Job Summary Writer",
    goal="Buat ringkasan bersih dan actionable dari internship yang ditemukan",
    backstory=(
        "Kamu nulis job summary yang langsung to the point. "
        "Format per opportunity: nama company, posisi, deadline, link apply, "
        "dan 1 kalimat kenapa cocok. No fluff."
    ),
    llm=llm,
    verbose=True,
)

# ── TASKS ────────────────────────────────────────────────────────────────────

scout_task = Task(
    description=(
        "Cari ML/AI internship yang currently open (2026). "
        "Gunakan minimal 4 search query berbeda:\n"
        "1. 'ML engineer intern 2026 remote apply now'\n"
        "2. 'AI research internship 2026 open application'\n"
        "3. 'NLP intern 2026 HuggingFace Cohere Mistral'\n"
        "4. 'machine learning internship 2026 international students'\n"
        "Return: list peluang dengan nama company, posisi, link, dan deadline kalau ada."
    ),
    expected_output="List 8-12 internship opportunities dengan company, posisi, link, deadline",
    agent=scout,
)

filter_task = Task(
    description=(
        "Dari list yang ditemukan Scout, filter dan rank TOP 5 yang paling cocok. "
        "Buka link tiap opportunity dan cek: masih open? ada syarat citizenship? "
        "Rank berdasarkan: relevansi skill match + kemungkinan lolos + prestige company. "
        "Highlight kalau ada yang mirip Cohere (yang udah diapply sebelumnya)."
    ),
    expected_output="Top 5 internship yang difilter + alasan singkat kenapa cocok + status open/closed",
    agent=filter_agent,
    context=[scout_task],
)

summary_task = Task(
    description=(
        f"Buat weekly job digest untuk tanggal {date.today().strftime('%d %B %Y')}.\n\n"
        "Format:\n"
        "# Internship Digest — [tanggal]\n\n"
        "## Top Picks\n"
        "Untuk tiap opportunity (max 5):\n"
        "**[Company] — [Posisi]**\n"
        "- Link: ...\n"
        "- Deadline: ...\n"
        "- Why apply: 1 kalimat\n\n"
        "## Already Applied\n"
        "- Cohere ML Intern (applied 2026-06-20)\n"
        "- Cohere SWE Intern (applied 2026-06-20)\n\n"
        "## This Week Action\n"
        "1-2 hal yang harus dilakuin minggu ini soal job hunting."
    ),
    expected_output="Weekly internship digest dalam markdown, siap dibaca",
    agent=summarizer,
    context=[filter_task],
)

# ── CREW ─────────────────────────────────────────────────────────────────────

crew = Crew(
    agents=[scout, filter_agent, summarizer],
    tasks=[scout_task, filter_task, summary_task],
    verbose=True,
)

result = crew.kickoff()

print("\n" + "="*60)
print("INTERNSHIP DIGEST")
print("="*60)
print(result)

filename = f"jobs_{date.today().strftime('%Y-%m-%d')}.md"
with open(filename, "w") as f:
    f.write(str(result))
print(f"\n✓ Disimpan ke {filename}")
