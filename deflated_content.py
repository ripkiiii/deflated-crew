import os
from datetime import date
from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool

llm = LLM(
    model="zai/glm-4.7-flash",
    api_key=os.environ.get("ZAI_API_KEY", "fb4af394b79e400fa6277241bc3b7464.Q3ApMGJxs9flsPY5"),
    max_rpm=6,
)

digest_file = f"digest_{date.today().strftime('%Y-%m-%d')}.md"
file_tool = FileReadTool(file_path=digest_file)

# ── AGENTS ──────────────────────────────────────────────────────────────────

picker = Agent(
    role="Content Strategist",
    goal="Pilih insight terbaik dari research digest yang paling menarik untuk audiens Twitter/X",
    backstory=(
        "Kamu adalah content strategist untuk Deflated AI Studio — "
        "sebuah indie AI studio dari Indonesia yang build LLM dan dataset dari scratch. "
        "Kamu tau apa yang bikin developer dan AI researcher berhenti scroll: "
        "fakta yang surprising, angle yang unik, atau insight yang orang lain miss. "
        "Kamu pilih 1 topik terbaik dari digest untuk dijadiin thread."
    ),
    llm=llm,
    tools=[file_tool],
    verbose=True,
)

writer = Agent(
    role="Twitter Thread Writer",
    goal="Tulis thread X yang engaging, informatif, dan authentic dari sudut pandang indie AI builder Indonesia",
    backstory=(
        f"Kamu nulis thread Twitter untuk Deflated AI Studio. Sekarang tahun {date.today().year}. "
        "Voice-nya: CAMPUR Indo-Inggris — bukan full Indo, bukan full English. "
        "Contoh gaya WAJIB diikuti: 'QLoRA is insane. Basically kamu bisa fine-tune LLM di laptop biasa.' "
        "Contoh lain: 'Dataset Indo masih langka banget. That's exactly why we built this.' "
        "Build in public, jujur soal keterbatasan (free compute, solo builder), tapi confident. "
        "Bukan akademik, bukan marketing. Gaya Andrej Karpathy tapi versi Indo yang santai. "
        "Akun Bluesky: @deflatedxyz.bsky.social — pakai ini di CTA terakhir. "
        "LARANGAN KERAS: JANGAN tulis full English. Setiap tweet harus ada kata Indo. "
        "LARANGAN KERAS: JANGAN pakai markdown **bold** atau *italic*. Plain text only. "
        "PENTING: emoji bendera Indonesia = 🇮🇩. BUKAN 🇮🇳 (itu India)."
    ),
    llm=llm,
    verbose=True,
)

editor = Agent(
    role="Social Media Editor",
    goal="Polish thread supaya maksimal engagement — hook kuat, flow enak, call to action jelas",
    backstory=(
        "Kamu editor thread Twitter yang obsesif sama first tweet. "
        "Kamu tau kalau tweet pertama gagal grab attention, thread mati. "
        "Kamu juga mastiin tiap tweet max 280 karakter, ada numbering (1/n), "
        "dan thread nutup dengan CTA yang natural bukan maksa. "
        "WAJIB: Hapus semua markdown formatting (**bold**, *italic*) — plain text only. "
        "WAJIB: Pastikan bahasa campur Indo-English, bukan full Indonesia. "
        "WAJIB: Emoji bendera Indonesia = 🇮🇩, bukan 🇮🇳."
    ),
    llm=llm,
    verbose=True,
)

# ── TASKS ────────────────────────────────────────────────────────────────────

pick_task = Task(
    description=(
        f"Baca file '{digest_file}' dan pilih 1 topik/paper yang paling menarik untuk dijadiin thread Twitter. "
        "Kriteria: surprising, punya angle unik, relevan buat developer/researcher Indo, "
        "atau ada insight yang actionable. "
        "Jelaskan kenapa topik ini yang dipilih dan apa angle thread-nya."
    ),
    expected_output="1 topik terpilih + alasan + angle yang akan dipakai untuk thread",
    agent=picker,
)

write_task = Task(
    description=(
        "Tulis thread Twitter (8-12 tweets) berdasarkan topik yang dipilih. "
        "Format tiap tweet: [nomor/total] isi tweet\n\n"
        "Aturan:\n"
        "- Tweet 1: hook yang bikin orang berhenti scroll\n"
        "- Tweet 2-3: konteks / masalah yang ada\n"
        "- Tweet 4-8: insight utama, dipecah per poin\n"
        "- Tweet 9-11: so what? apa yang bisa dilakuin\n"
        "- Tweet terakhir: CTA natural (follow, reply, atau share)\n\n"
        "Voice: casual Indo-English mix, build in public, dari perspektif solo builder. "
        "Mention @deflatedxyz.bsky.social sebagai akun Deflated di Bluesky."
    ),
    expected_output="Thread lengkap 8-12 tweets, siap copy-paste ke Twitter",
    agent=writer,
    context=[pick_task],
)

edit_task = Task(
    description=(
        "Review dan polish thread dari Writer:\n"
        "1. Pastiin tweet 1 assalting banget sebagai hook\n"
        "2. Cek tiap tweet max 280 karakter\n"
        "3. Pastiin ada numbering yang konsisten (1/n format)\n"
        "4. Flow antar tweet harus smooth\n"
        "5. CTA di akhir natural, bukan maksa\n\n"
        "Return thread final yang udah dipoles, siap post."
    ),
    expected_output="Thread final yang sudah dipoles, format rapi, siap post ke X/Twitter",
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
