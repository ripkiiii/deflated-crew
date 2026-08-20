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
ap.add_argument(
    "--date",
    default=None,
    help="YYYY-MM-DD, or comma-separated list of dates, to delete posts from (default: today)",
)
args = ap.parse_args()
if args.date:
    target_dates = {dateparser.parse(d.strip()).date() for d in args.date.split(",")}
else:
    target_dates = {date.today()}

client = Client()
client.login(HANDLE, APP_PASSWORD)

# get_author_feed returns individual thread replies as separate items too,
# so a handful of threads can easily exceed one page — paginate through
# everything instead of trusting a single limit=100 call.
deleted_by_date = {d: 0 for d in target_dates}
cursor = None

while True:
    feed = client.get_author_feed(actor=HANDLE, limit=100, cursor=cursor)
    if not feed.feed:
        break

    for item in feed.feed:
        post = item.post
        created_at = dateparser.parse(post.record.created_at).date()
        if created_at in target_dates:
            client.delete_post(post.uri)
            print(f"✓ Deleted [{created_at}]: {post.uri}")
            deleted_by_date[created_at] += 1

    cursor = feed.cursor
    if not cursor:
        break

total = sum(deleted_by_date.values())
if total == 0:
    print(f"Ga ada post di {sorted(target_dates)}.")
else:
    print(f"\n🗑️ {total} post dihapus total:")
    for d, n in sorted(deleted_by_date.items()):
        print(f"  {d}: {n} post")
