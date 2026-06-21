import os
from datetime import date
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

os.environ["SERPER_API_KEY"] = os.environ.get("SERPER_API_KEY", "1c7234686d677b501f58d6c7a555da8d5b471004")

llm = LLM(model="zai/glm-4.7-flash", api_key=os.environ.get("ZAI_API_KEY", "fb4af394b79e400fa6277241bc3b7464.Q3ApMGJxs9flsPY5"))
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# ── AGENTS ──────────────────────────────────────────────────────────────────

scout = Agent(
    role="Research Scout",
    goal="Temukan paper dan artikel terbaru tentang NLP, Indonesian AI, dan low-resource language model",
    backstory=(
        "Kamu adalah scout riset yang obsesif. Setiap hari kamu menyisir ArXiv, HuggingFace, "
        "dan web untuk menemukan paper terbaru tentang NLP dan Indonesian language model. "
        "Kamu hanya peduli dengan yang relevan untuk membangun LLM bahasa Indonesia."
    ),
    llm=llm,
    tools=[search_tool],
    verbose=True,
)

analyst = Agent(
    role="Research Analyst",
    goal="Analisis dan filter paper yang paling relevan untuk IDK-1 dan Nala",
    backstory=(
        "Kamu adalah analis riset yang kritis. Dari daftar paper yang ditemukan Scout, "
        "kamu menentukan mana yang benar-benar berguna untuk: (1) training Indonesian LLM dari scratch, "
        "(2) fine-tuning model untuk domain spesifik seperti dokumen pemerintah, "
        "(3) dataset Indonesian. Kamu buang yang tidak relevan."
    ),
    llm=llm,
    tools=[scrape_tool],
    verbose=True,
)

summarizer = Agent(
    role="Research Summarizer",
    goal="Rangkum paper terpilih menjadi insight actionable yang bisa langsung dipakai",
    backstory=(
        "Kamu adalah summarizer yang efisien. Kamu mengubah paper akademik yang panjang "
        "menjadi ringkasan singkat yang bisa dibaca dalam 2 menit. "
        "Fokusmu: apa yang baru, kenapa penting, dan apa yang bisa langsung diimplementasi."
    ),
    llm=llm,
    verbose=True,
)

# ── TASKS ────────────────────────────────────────────────────────────────────

scout_task = Task(
    description=(
        "Cari paper dan artikel terbaru (2025-2026) tentang:\n"
        "1. Indonesian NLP / Indonesian language model\n"
        "2. Low-resource language model training\n"
        "3. QLoRA / efficient fine-tuning untuk small LLM\n"
        "4. Indonesian dataset (CommonCrawl, Wikipedia, government docs)\n\n"
        "Gunakan search tool. Cari minimal 3 query berbeda. "
        "Return: list judul + link + snippet singkat."
    ),
    expected_output="List 8-10 paper/artikel terbaru dengan judul, link, dan 1 kalimat deskripsi",
    agent=scout,
)

analyst_task = Task(
    description=(
        "Dari list yang ditemukan Scout, pilih TOP 3-5 yang paling relevan untuk:\n"
        "- IDK-1: Indonesian LLM 100M parameter dari scratch\n"
        "- Nala: fine-tuned model untuk dokumen pemerintah Indonesia\n\n"
        "Untuk setiap paper yang dipilih, buka linknya dan baca isinya. "
        "Jelaskan kenapa paper ini relevan dan apa yang bisa dipelajari."
    ),
    expected_output="Top 3-5 paper dengan alasan relevansi dan poin utama yang bisa dipakai",
    agent=analyst,
    context=[scout_task],
)

summarizer_task = Task(
    description=(
        "Buat daily research digest untuk Deflated AI Studio.\n"
        "Format:\n"
        "# Deflated Research Digest — {today}\n\n"
        "Untuk setiap paper (top 3-5):\n"
        "## [Judul Paper]\n"
        "**Link:** ...\n"
        "**TL;DR:** 2-3 kalimat apa isi papernya\n"
        "**Relevan untuk:** IDK-1 / Nala / Dataset\n"
        "**Actionable:** apa yang bisa langsung dicoba atau dipelajari\n\n"
        "Tutup dengan **Bottom Line:** 1 paragraf insight keseluruhan hari ini."
    ).format(today=date.today().strftime("%d %B %Y")),
    expected_output="Research digest lengkap dalam format markdown, siap dibaca",
    agent=summarizer,
    context=[analyst_task],
)

# ── CREW ─────────────────────────────────────────────────────────────────────

crew = Crew(
    agents=[scout, analyst, summarizer],
    tasks=[scout_task, analyst_task, summarizer_task],
    verbose=True,
)

result = crew.kickoff()

print("\n" + "="*60)
print("DEFLATED RESEARCH DIGEST")
print("="*60)
print(result)

filename = f"digest_{date.today().strftime('%Y-%m-%d')}.md"
with open(filename, "w") as f:
    f.write(str(result))
print(f"\n✓ Disimpan ke {filename}")
