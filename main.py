from fastapi import FastAPI, HTTPException
import requests
from pytube import YouTube
from tiktokpy import TikTok

app = FastAPI()

def to_supported_format(url):
    if "list=" in url:
        playlist_id = url[url.index("list=") + 5:]
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    return url

@app.post("/instagram")
def instagram_endpoint(url: str):
    split_url = url.split("/")
    ig_code = split_url[4]
    ig_url = f"https://www.instagram.com/p/{ig_code}/?__a=1"

    response = requests.get(ig_url)
    if response.status_code == 200:
        json_data = response.json()
        if "graphql" in json_data:
            shortcode_media = json_data["graphql"]["shortcode_media"]
            post_type = shortcode_media["__typename"]

            if post_type not in ["GraphImage", "GraphSidecar", "GraphVideo"]:
                raise HTTPException(status_code=400, detail="No Post Type Found")

            display_url = shortcode_media["display_url"]
            edge_media_to_caption = shortcode_media["edge_media_to_caption"]["edges"]
            caption = edge_media_to_caption[0]["node"]["text"] if edge_media_to_caption else ""
            owner_data = shortcode_media["owner"]
            total_media = owner_data["edge_owner_to_timeline_media"]["count"]
            hashtags = caption.split("#")[1:]

            if post_type == "GraphImage":
                data_download = display_url
            elif post_type == "GraphSidecar":
                data_download = [
                    {
                        "is_video": post["node"]["is_video"],
                        "placeholder_url": post["node"]["video_url"]
                        if post["node"]["is_video"]
                        else post["node"]["display_url"],
                    }
                    for post in shortcode_media["edge_sidecar_to_children"]["edges"]
                ]
            else:  # post_type == "GraphVideo"
                data_download = shortcode_media["owner"]["video_url"]

            result = {
                "status": "success",
                "postType": post_type,
                "displayUrl": display_url,
                "caption": caption,
                "owner": owner_data["username"],
                "is_verified": owner_data["is_verified"],
                "profile_pic": owner_data["profile_pic_url"],
                "full_name": owner_data["full_name"],
                "is_private": owner_data["is_private"],
                "total_media": total_media,
                "hashtags": hashtags,
                "dataDownload": data_download,
            }
            return result
        else:
            raise HTTPException(status_code=400, detail="URL Failed")
    else:
        raise HTTPException(status_code=400, detail="Error on getting response")

@app.post("/youtube")
def youtube_endpoint(url: str):
    try:
        yt = YouTube(url)
        info = yt.streams.first()

        result = {
            "status": "success",
            "ownerUrl": yt.author_url,
            "ownerId": yt.author_id,
            "channelUrl": yt.channel_url,
            "uploader": yt.author,
            "totalViews": yt.views,
            "urlId": yt.video_id,
            "thumbnail": yt.thumbnail_url,
            "description": yt.description,
            "filename": info.title,
            "duration": yt.length,
            "title": info.title,
            "categories": yt.categories,
            "dataFormats": [
                {
                    "dataDownload": info.url,
                    "format": info.mime_type,
                    "ext": info.extension,
                    "filesize": info.filesize,
                }
            ],
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/youtube-playlist")
def youtube_playlist_endpoint(url: str):
    url = to_supported_format(url)
    yt = YouTube(url)

    data_downloads = []

    for video_info in yt.streams:
        data_downloads.append({
            "ownerUrl": yt.author_url,
            "ownerId": yt.author_id,
            "channelUrl": yt.channel_url,
            "uploader": yt.author,
            "totalViews": yt.views,
            "urlId": yt.video_id,
            "thumbnail": yt.thumbnail_url,
            "description": yt.description,
            "filename": video_info.title,
            "duration": yt.length,
            "title": video_info.title,
            "categories": yt.categories,
            "dataFormats": [
                {
                    "dataDownload": video_info.url,
                    "format": video_info.mime_type,
                    "ext": video_info.extension,
                    "filesize": video_info.filesize,
                }
            ],
        })

    return {"status": "success", "dataDownloads": data_downloads}

@app.post("/tiktok")
def tiktok_endpoint(url: str):
    try:
        tiktok_video = TikTok(url)

        result = {
            "status": "success",
            "headers": tiktok_video.headers,
            "username": tiktok_video.authorMeta["name"],
            "name": tiktok_video.authorMeta["nickName"],
            "profilePic": tiktok_video.authorMeta["avatar"],
            "description": tiktok_video.text,
            "thumbnail": tiktok_video.imageUrl,
            "format": tiktok_video.videoMeta["ratio"],
            "urlDownload": tiktok_video.videoUrl,
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Add similar routes for /facebook and /dailymotion as needed
