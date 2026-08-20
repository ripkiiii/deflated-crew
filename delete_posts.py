import argparse
import os
from datetime import date

from atproto import Client
from dateutil import parser as dateparser

if "BLUESKY_APP_PASSWORD" not in os.environ:
    raise SystemExit("BLUESKY_APP_PASSWORD not set in environment")

HANDLE = os.environ.get("BLUESKY_HANDLE", "deflatedxyz.bsky.social")
APP_PASSWORD = os.environ["BLUESKY_APP_PASSWORD"]

ap = argparse.ArgumentParser()
ap.add_argument("--date", default=None, help="YYYY-MM-DD to delete posts from (default: today)")
args = ap.parse_args()
target_date = dateparser.parse(args.date).date() if args.date else date.today()

client = Client()
client.login(HANDLE, APP_PASSWORD)

feed = client.get_author_feed(actor=HANDLE, limit=100)
posts = feed.feed

deleted = 0

for item in posts:
    post = item.post
    created_at = dateparser.parse(post.record.created_at)
    if created_at.date() == target_date:
        client.delete_post(post.uri)
        print(f"✓ Deleted: {post.uri}")
        deleted += 1

if deleted == 0:
    print(f"Ga ada post di {target_date}.")
else:
    print(f"\n🗑️ {deleted} post di {target_date} dihapus.")
