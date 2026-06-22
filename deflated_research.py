import os
from datetime import date
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

os.environ["SERPER_API_KEY"] = os.environ.get("SERPER_API_KEY", "1c7234686d677b501f58d6c7a555da8d5b471004")

llm = LLM(
    model="gemini/gemini-2.5-flash-lite",
    api_key=os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6J1a0m4-i8wAII5X_yol1O3m8epsOATGa4w_gR3Jn0Rgw"),
    max_tokens=2048,
    max_rpm=4,
)
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# ── AGENTS ──────────────────────────────────────────────────────────────────

scout = Agent(
    role="Research Scout",
    goal="Temukan paper dan artikel terbaru tentang NLP, Indonesian AI, dan Small Language Models (SLM)",
    backstory=(
        "Kamu adalah scout riset yang obsesif. Setiap hari kamu menyisir ArXiv, HuggingFace, "
        "dan web untuk menemukan paper terbaru tentang NLP, SLM, dan Indonesian language model. "
        "Kamu hanya peduli dengan yang relevan untuk membangun SLM bahasa Indonesia dari scratch."
    ),
    llm=llm,
    tools=[search_tool],
    verbose=True,
)

analyst = Agent(
    role="Research Analyst",
    goal="Analisis dan filter paper yang paling relevan untuk IDK-1, Nala, dan PRENA",
    backstory=(
        "Kamu adalah analis riset yang kritis. Dari daftar paper yang ditemukan Scout, "
        "kamu menentukan mana yang benar-benar berguna untuk: "
        "(1) IDK-1 — Indonesian SLM (Small Language Model) 100M param dari scratch, "
        "(2) Nala — fine-tuned SLM untuk dokumen pemerintah Indonesia, "
        "(3) PRENA — nano LM + dataset PR Indonesia untuk riset akademik (target paper Scopus). "
        "SLM lebih relevan dari LLM untuk ketiga proyek ini. Kamu buang yang tidak relevan."
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
        "1. Indonesian NLP / Indonesian SLM (Small Language Model)\n"
        "2. Low-resource SLM training / efficient pre-training\n"
        "3. QLoRA / LoRA / PEFT untuk SLM fine-tuning\n"
        "4. Indonesian dataset (CommonCrawl, Wikipedia, government docs, PR/media)\n\n"
        "Gunakan search tool. Cari minimal 3 query berbeda. "
        "Return: list judul + link + snippet singkat."
    ),
    expected_output="List 8-10 paper/artikel terbaru dengan judul, link, dan 1 kalimat deskripsi",
    agent=scout,
)

analyst_task = Task(
    description=(
        "Dari list yang ditemukan Scout, pilih TOP 3-5 yang paling relevan untuk:\n"
        "- IDK-1: Indonesian SLM 100M parameter dari scratch (decoder-only, LLaMA-style)\n"
        "- Nala: fine-tuned SLM untuk dokumen pemerintah Indonesia\n"
        "- PRENA: nano LM + dataset PR Indonesia, untuk riset akademik\n\n"
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
