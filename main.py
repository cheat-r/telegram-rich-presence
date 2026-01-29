from quart import Quart, request
from client import update_status, delete_status, start_client, stop_client, delete_cache
from tags import tag_change

cache_title = None
cache_artist = None

app = Quart(__name__)

@app.before_serving
async def _startup():
    await start_client()

@app.after_serving
async def _shutdown():
    await delete_status()
    await delete_cache()
    await stop_client()

@app.route("/trp/premid", methods=["POST"])
async def webhook():
    global cache_artist, cache_title
    data = await request.get_json(silent=True)
    active_activity = data['active_activity']
    if active_activity:
        if active_activity['name'] == 'YouTube':
            title = f"{active_activity['details']}"
            artist = f"{active_activity['name']} | {active_activity['state']}"
            if title == cache_title and artist == cache_artist:
                return "OK", 200
            cache_title = title
            cache_artist = artist
            sample = tag_change(title, artist)
            await update_status(sample, active_activity['assets']['large_image'])
    else:
        await delete_status()
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1225)
