# Playing around with YouTube Music API

[Docs](https://ytmusicapi.readthedocs.io/en/stable/setup/index.html)
[Repo]()


## setup

unbuntu
```
python3 -m pip install --user --upgrade pip
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Windows
```
python3.exe -m pip install --upgrade pip
python3 -m venv env
.\env\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Connection setup

```
pip install ytmusicapi
ytmusicapi oauth

```


```
accept: */*
accept-encoding: gzip, deflate, br
accept-language: en-US,en;q=0.9,fr;q=0.8
authorization: SAPISIDHASH 1615377231_8cf76367d698879713878392128797050205a232
content-length: 709
content-type: application/json
cookie: VISITOR_INFO1_LIVE=NDMD63E-d9U; _ga=GA1.2.1277147972.1587138006; LOGIN_INFO=AFmmF2swRAIgK8QBCNxzHM5lmIW7yxRvjzZvZf7dp7sFAQ2a59iQVBkCIGb6FF5Nhax6H__1X9jUIY9Dc06YG5thjWirgyRZ0hLf:QUQ3MjNmeGRYN2wwZF9fM3JWSmg4R3FwcjZxZ25uQlJOaVZTRl81VnNVLWhNSnZQZUlyNHNiNkoya2hUbjFoUzZ4Wkw1N3pfTzBIN18wRVU2R0w1dEU0UVRnSl9WVVVPcXJEUnBlRjA2VVM1NEtUbnR2ZG90R3BzeTZSVVpLWVRxSzY5NlQtaXN4SEJtRl84ZmNEaTgtQnZ2WmtZa245YUpsb0MxbXN2bUNuYUZscXpUcndoQVMw; YTV_CLC=locsrc=1&locs=2&tz=America%2FChicago; _gcl_au=1.1.911543841.1613763330; YSC=ZI-0fuWqZNM; PREF=f6=80&volume=20&tz=America.Chicago&library_tab_browse_id=FEmusic_liked_videos&location_based_recommendations=2&al=en&f5=30; SID=7gf4MCUjZytqrlOjJM2k5ForBuSEZXoUOSx8wbpUjR06zubGDHybnzUIsPHMBQTy1h1yVQ.; __Secure-3PSID=7gf4MCUjZytqrlOjJM2k5ForBuSEZXoUOSx8wbpUjR06zubG-xYtvjeVLFvps3DDReNEZQ.; HSID=AdGguou7b-fqZRnOA; SSID=AfBFbsni23luDn3as; APISID=A_D4z00suYV5JF5a/Ad_AEWyDAOUEFW-XB; SAPISID=sWVneQb5_JcKoXmG/AjTTWoIfI4YMopuqy; __Secure-3PAPISID=sWVneQb5_JcKoXmG/AjTTWoIfI4YMopuqy; SIDCC=AJi4QfHjzdv5AIZkh0opwTrwzBnFbsnD7upGCbSy0J-7uZlU9gZxpaxmFs6TkptwhsKoUA5uqSfi; __Secure-3PSIDCC=AJi4QfGaEDLu40QTc2d6cWGLH9z35TcWWP4TD7xCpGv1kYnizNmwBc_DaJnqVP9zpR0OkRstT7Wm
origin: https://music.youtube.com
referer: https://music.youtube.com/library/songs
sec-ch-ua: "Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"
sec-ch-ua-mobile: ?0
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36
x-client-data: CJa2yQEIo7bJAQipncoBCPjHygEIpuHKAQjGnMsBCOOcywEIqZ3LAQ==
Decoded:
message ClientVariations {
  // Active client experiment variation IDs.
  repeated int32 variation_id = [3300118, 3300131, 3313321, 3318776, 3322022, 3329606, 3329635, 3329705];
}
x-goog-authuser: 0
x-goog-pageid: undefined
x-goog-visitor-id: CgtORE1ENjNFLWQ5VSj25aKCBg%3D%3D
x-origin: https://music.youtube.com
x-youtube-ad-signals: dt=1615377142893&flash=0&frm&u_tz=-360&u_his=3&u_java&u_h=1080&u_w=1920&u_ah=1055&u_aw=1920&u_cd=24&u_nplug=3&u_nmime=4&bc=31&bih=601&biw=1250&brdim=0%2C0%2C0%2C0%2C1920%2C0%2C1270%2C1055%2C1262%2C601&vis=1&wgl=true&ca_type=image&bid=ANyPxKoZl9Bu1YMssOOValDwCkrThbDRdVSvDdjCGk70tCKV1MP2i-x1D5zm4YmctxQwQDdNP9zCvIeXacyKARLXMmwc5_5vVQ
x-youtube-client-name: 67
x-youtube-client-version: 0.1
x-youtube-device: cbr=Chrome&cbrver=89.0.4389.82&ceng=WebKit&cengver=537.36&cos=X11&cplatform=DESKTOP
x-youtube-identity-token: QUFFLUhqbEdNbUk0ZWRNTi12SHcwcl9mbk1lZWZBbm1FZ3w=
x-youtube-page-cl: 360656655
x-youtube-page-label: youtube.music.web.client_20210303_00_RC00
x-youtube-time-zone: America/Chicago
x-youtube-utc-offset: -360
```