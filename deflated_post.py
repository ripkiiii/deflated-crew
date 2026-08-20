import os
from atproto import Client, models
from datetime import date

if "BLUESKY_APP_PASSWORD" not in os.environ:
    raise SystemExit("BLUESKY_APP_PASSWORD not set in environment")

HANDLE = os.environ.get("BLUESKY_HANDLE", "deflatedxyz.bsky.social")
APP_PASSWORD = os.environ["BLUESKY_APP_PASSWORD"]

def clean_tweet(text):
    import re
    # strip markdown bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # fix India flag → Indonesia flag
    text = text.replace('🇮🇳', '🇮🇩')
    return text.strip()

def parse_thread(filename):
    with open(filename, "r") as f:
        content = f.read()

    import re
    tweets = []
    blocks = [b.strip() for b in re.split(r'\n\s*\n', content.strip()) if b.strip()]
    # Matches: 1/9, [1/9], **1/9**, (1/9) — with optional newline after
    NUMBER_RE = re.compile(r'^\[?\*{0,2}\d+/\d+\*{0,2}\]?\s*', re.MULTILINE)
    for block in blocks:
        m = NUMBER_RE.match(block)
        if m:
            tweet_text = block[m.end():].strip()
            if tweet_text:
                tweets.append(clean_tweet(tweet_text))
    return tweets

def post_thread(tweets):
    client = Client()
    client.login(HANDLE, APP_PASSWORD)

    root = None
    parent = None

    for i, text in enumerate(tweets):
        if i == 0:
            response = client.send_post(text=text)
            root = {"cid": response.cid, "uri": response.uri}
            parent = {"cid": response.cid, "uri": response.uri}
        else:
            reply_ref = models.AppBskyFeedPost.ReplyRef(
                root=models.ComAtprotoRepoStrongRef.Main(cid=root["cid"], uri=root["uri"]),
                parent=models.ComAtprotoRepoStrongRef.Main(cid=parent["cid"], uri=parent["uri"])
            )
            response = client.send_post(text=text, reply_to=reply_ref)
            parent = {"cid": response.cid, "uri": response.uri}
        print(f"✓ Posted [{i+1}/{len(tweets)}]")

    print(f"\n🚀 Thread live: https://bsky.app/profile/{HANDLE}")

if __name__ == "__main__":
    filename = f"thread_{date.today().strftime('%Y-%m-%d')}.md"
    tweets = parse_thread(filename)
    print(f"→ {len(tweets)} tweets ditemukan dari {filename}")
    post_thread(tweets)
