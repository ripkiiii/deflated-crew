from atproto import Client
from datetime import date, timezone
from dateutil import parser as dateparser

HANDLE = "deflatedxyz.bsky.social"
APP_PASSWORD = "jgn3-kzui-ia7t-p4mg"

client = Client()
client.login(HANDLE, APP_PASSWORD)

feed = client.get_author_feed(actor=HANDLE, limit=100)
posts = feed.feed

today = date.today()
deleted = 0

for item in posts:
    post = item.post
    created_at = dateparser.parse(post.record.created_at)
    if created_at.date() == today:
        client.delete_post(post.uri)
        print(f"✓ Deleted: {post.uri}")
        deleted += 1

if deleted == 0:
    print("Ga ada post hari ini.")
else:
    print(f"\n🗑️ {deleted} posts hari ini dihapus.")
