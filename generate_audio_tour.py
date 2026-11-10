import asyncio
import os
import json
import edge_tts
import re

VOICE_PRESETS = [
    # 沉穩專業男聲
    ("zh-CN-YunxiNeural", "+0%", "+0Hz", "_male", False),
    # 溫潤柔和女聲
    ("zh-TW-HsiaoYuNeural", "-5%", "-2Hz", "_zen_female", False),
    # 現代俐落女聲 (預設)
    ("zh-TW-HsiaoChenNeural", "+0%", "+0Hz", "", False),
]

def format_zen_script(script: str) -> str:
    """句間加入適度停頓，結尾保持自然流暢收尾"""
    text = re.sub(r"。(?=.)", "。…… ", script)
    text = re.sub(r"；(?=.)", "；… ", text)
    return text

async def generate():
    data_path = os.path.join('data', 'harvard_complete_data.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs(os.path.join('static', 'audio'), exist_ok=True)

    # Ensure audio_file path is set for all chapters
    chapter_map = {
        'tour-welcome': '/static/audio/tour_welcome.mp3',
        'tour-about': '/static/audio/tour_about.mp3',
        'tour-network': '/static/audio/tour_network.mp3',
        'tour-products': '/static/audio/tour_products.mp3',
        'tour-specs': '/static/audio/tour_specs.mp3',
        'tour-machining': '/static/audio/tour_machining.mp3',
        'tour-cases': '/static/audio/tour_cases.mp3',
        'tour-tech': '/static/audio/tour_tech.mp3',
        'tour-closing': '/static/audio/tour_closing.mp3',
    }

    modified = False
    for ch in data.get('tour_chapters', []):
        cid = ch.get('id')
        if cid in chapter_map and ch.get('audio_file') != chapter_map[cid]:
            ch['audio_file'] = chapter_map[cid]
            modified = True

    if modified:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Updated tour_chapters.audio_file paths in harvard_complete_data.json")

    for voice_name, rate, pitch, suffix, is_zen in VOICE_PRESETS:
        for ch in data['tour_chapters']:
            base_path = ch['audio_file'].lstrip('/')
            root, ext = os.path.splitext(base_path)
            out_path = f"{root}{suffix}{ext}" if suffix else base_path

            if os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
                print(f"Skipping existing [{ch['title']}] -> {out_path} ({os.path.getsize(out_path)} bytes)")
                continue

            script_text = format_zen_script(ch['script']) if is_zen else ch['script']
            print(f"Generating [{ch['title']}] ({voice_name}) -> {out_path}...")
            try:
                tts = edge_tts.Communicate(script_text, voice_name, rate=rate, pitch=pitch)
                await tts.save(out_path)
                print(f"  -> Saved {out_path} ({os.path.getsize(out_path)} bytes)")
            except Exception as e:
                print(f"  -> Error generating {out_path}: {e}")

if __name__ == '__main__':
    asyncio.run(generate())
    print("All Harvard audio tour chapters generated successfully!")

