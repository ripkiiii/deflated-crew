import os
from datetime import date
from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool

llm = LLM(
    model="groq/llama3-8b-8192",
    api_key=os.environ.get("GROQ_API_KEY", "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"),
    max_tokens=1024,
)

digest_file = f"digest_{date.today().strftime('%Y-%m-%d')}.md"
file_tool = FileReadTool(file_path=digest_file)

# ── AGENTS ──────────────────────────────────────────────────────────────────

strategist = Agent(
    role="Blog Strategist",
    goal="Pilih topik terbaik dari digest untuk dijadiin artikel blog yang menarik",
    backstory=(
        "Kamu strategist untuk Deflated AI Studio blog. "
        "Kamu tau topik mana yang worth ditulis panjang vs cuma worth di thread. "
        "Kriteria: ada angle unik, bisa di-expand jadi 500-700 kata, "
        "relevan buat Indo AI community, dan punya insight yang ga obvious."
    ),
    llm=llm,
    tools=[file_tool],
    verbose=True,
)

writer = Agent(
    role="Blog Writer",
    goal="Tulis artikel blog yang honest, casual, dan insightful tentang Indo AI",
    backstory=(
        f"Kamu nulis blog untuk deflated.xyz — personal AI research studio dari Indonesia. Tahun {date.today().year}. "
        "Voice-nya: English jelek tapi jujur, build in public, solo builder. "
        "Gaya: Andrej Karpathy meets Paul Graham tapi lebih santai dan lebih Indo context. "
        "Struktur artikel: judul kuat → 1 paragraf hook → beberapa section pendek → takeaway. "
        "Panjang: 500-700 kata. No fluff, no filler. "
        "JANGAN pakai markdown headers yang lebay. Cukup ## untuk section. "
        "Tulis seolah-olah lo lagi ngobrol sama fellow developer, bukan presentasi."
    ),
    llm=llm,
    verbose=True,
)

editor = Agent(
    role="Blog Editor",
    goal="Polish artikel supaya siap publish — tone konsisten, no filler, ending kuat",
    backstory=(
        "Kamu editor blog yang obsesif sama opening paragraph. "
        "Kalau opening ga hook dalam 2 kalimat pertama, lo rewrite. "
        "Lo juga mastiin: tidak ada kalimat filler, ending ada call-to-action natural, "
        "dan tone konsisten casual tapi substantif dari awal sampai akhir. "
        "Format output: judul di baris pertama, lalu artikel lengkap."
    ),
    llm=llm,
    verbose=True,
)

# ── TASKS ────────────────────────────────────────────────────────────────────

strategy_task = Task(
    description=(
        f"Baca file '{digest_file}' dan pilih 1 topik yang paling worth dijadiin artikel blog panjang. "
        "Bukan thread — artikel yang bisa di-expand jadi 500-700 kata dengan depth. "
        "Tentukan: topik, angle spesifik, dan outline kasar (3-4 poin utama)."
    ),
    expected_output="Topik terpilih + angle + outline 3-4 poin",
    agent=strategist,
)

write_task = Task(
    description=(
        "Tulis artikel blog lengkap berdasarkan topik dan outline dari Strategist. "
        "Format:\n"
        "# [Judul Artikel]\n\n"
        "[Isi artikel 500-700 kata]\n\n"
        "Gunakan ## untuk section headers. "
        "Opening harus langsung grab attention. "
        "Ending harus ada takeaway atau pertanyaan yang bikin reader mikir."
    ),
    expected_output="Artikel blog lengkap 500-700 kata dalam markdown",
    agent=writer,
    context=[strategy_task],
)

edit_task = Task(
    description=(
        "Review dan polish artikel dari Writer:\n"
        "1. Opening 2 kalimat pertama harus langsung hook — rewrite kalau perlu\n"
        "2. Hapus semua kalimat filler ('As we can see...', 'It is important to note...')\n"
        "3. Pastiin tone casual tapi substantif dari awal sampai akhir\n"
        "4. Ending harus kuat — takeaway atau pertanyaan reflektif\n"
        "5. Cek panjang: 500-700 kata\n\n"
        "Return artikel final yang siap publish."
    ),
    expected_output="Artikel final siap publish dalam markdown, judul di baris pertama",
    agent=editor,
    context=[write_task],
)

# ── CREW ─────────────────────────────────────────────────────────────────────

crew = Crew(
    agents=[strategist, writer, editor],
    tasks=[strategy_task, write_task, edit_task],
    verbose=True,
)

result = crew.kickoff()

print("\n" + "="*60)
print("DEFLATED BLOG POST — SIAP PUBLISH")
print("="*60)
print(result)

filename = f"blog_{date.today().strftime('%Y-%m-%d')}.md"
with open(filename, "w") as f:
    f.write(str(result))
print(f"\n✓ Disimpan ke {filename}")
