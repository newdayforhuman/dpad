import mlx_whisper, glob, os, datetime

files = sorted(glob.glob(os.path.expanduser('~/recordings/*.m4a')))

def recorded_date(path):
    # macOS creation date ("birth time"); falls back to modified date elsewhere
    st = os.stat(path)
    ts = getattr(st, 'st_birthtime', st.st_mtime)
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

def header(audio_path):
    return f"=== {os.path.basename(audio_path)} — recorded {recorded_date(audio_path)} ==="

# Transcribe only recordings that don't have a transcript yet.
# (To force a redo of one clip, delete its .txt and run again.)
for f in files:
    txt = f.rsplit('.m4a', 1)[0] + '.txt'
    if os.path.exists(txt):
        print(f"already done, skipping: {os.path.basename(f)}", flush=True)
        continue
    print(f"\n{header(f)}", flush=True)
    r = mlx_whisper.transcribe(
        f,
        path_or_hf_repo='mlx-community/whisper-large-v3-mlx',
        condition_on_previous_text=False
    )
    text = r['text'].strip()
    print(text, flush=True)
    with open(txt, 'w') as fh:
        fh.write(f"{header(f)}\n{text}\n")

# Rebuild the combined file from every transcript, oldest recording first.
# Older .txt files from before this change have no header line, so add one.
combined = []
for f in sorted(files, key=lambda p: getattr(os.stat(p), 'st_birthtime', os.stat(p).st_mtime)):
    txt = f.rsplit('.m4a', 1)[0] + '.txt'
    if not os.path.exists(txt):
        continue
    with open(txt) as fh:
        content = fh.read().strip()
    if not content.startswith('==='):
        content = f"{header(f)}\n{content}"
    combined.append(content + "\n")

with open(os.path.expanduser('~/recordings/ALL_transcripts.txt'), 'w') as fh:
    fh.write("\n".join(combined))

print("\n\nDONE → ~/recordings/ALL_transcripts.txt", flush=True)
