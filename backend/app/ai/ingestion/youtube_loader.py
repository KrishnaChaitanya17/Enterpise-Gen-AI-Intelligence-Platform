from langcahin.document_loaders import YoutubeLoader

def load_youtube(video_url: str):
    loader = YoutubeLoader.from_youtube_url(
        video_url,
        add_video_info = True
    )

    docs = loader.load()

    for d in docs:
        d.metadata.update({
            "source": video_url,
            "type": "youtube"
        })

    return docs