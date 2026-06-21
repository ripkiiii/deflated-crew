from atproto import Client

HANDLE = "deflatedxyz.bsky.social"
APP_PASSWORD = "jgn3-kzui-ia7t-p4mg"

client = Client()
client.login(HANDLE, APP_PASSWORD)

feed = client.get_author_feed(actor=HANDLE, limit=100)
posts = feed.feed

if not posts:
    print("Ga ada post.")
else:
    for item in posts:
        uri = item.post.uri
        client.delete_post(uri)
        print(f"✓ Deleted: {uri}")
    print(f"\n🗑️ {len(posts)} posts dihapus.")
