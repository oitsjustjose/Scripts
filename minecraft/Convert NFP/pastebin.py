import requests

_KEY = "xxxxxx"  # TODO: Provide this key on your own!


def upload(nfp_contents: str) -> str:
    data = {"api_dev_key": _KEY, "api_paste_code": nfp_contents, "api_option": "paste"}

    resp = requests.post("https://pastebin.com/api/api_post.php", data=data)
    if resp.status_code == 200:
        return resp.text.replace("https://pastebin.com/", "")
    return f"FAILURE: {resp.text}"
