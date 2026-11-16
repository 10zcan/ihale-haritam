import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re
from datetime import datetime

ILLER = [
    "Adana","Adıyaman","Afyon","Ağrı","Amasya","Ankara","Antalya","Artvin","Aydın","Balıkesir",
    "Bilecik","Bingöl","Bitlis","Bolu","Burdur","Bursa","Çanakkale","Çankırı","Çorum","Denizli",
    "Diyarbakır","Edirne","Elazığ","Erzincan","Erzurum","Eskişehir","Gaziantep","Giresun","Gümüşhane","Hakkari",
    "Hatay","Isparta","Mersin","İstanbul","İzmir","Kars","Kastamonu","Kayseri","Kırklareli","Kırşehir",
    "Kocaeli","Konya","Kütahya","Malatya","Manisa","K.Maraş","Mardin","Muğla","Muş","Nevşehir",
    "Niğde","Ordu","Rize","Sakarya","Samsun","Siirt","Sinop","Sivas","Tekirdağ","Tokat",
    "Trabzon","Tunceli","Şanlıurfa","Uşak","Van","Yozgat","Zonguldak","Aksaray","Bayburt","Karaman",
    "Kırıkkale","Batman","Şırnak","Bartın","Ardahan","Iğdır","Yalova","Karabük","Kilis","Osmaniye","Düzce"
]

SORGULAR = [
    "kanalizasyon yapim isi ihalesi",
    "icme suyu altyapi yapim ihalesi",
    "dogalgaz elektrik altyapi kazi ihale",
    "dere islahi hafriyat yol yapim ihalesi"
]

try:
    with open("ihaleler.json", "r", encoding="utf-8") as f:
        mevcut = json.load(f)
except:
    mevcut = []

bugun = datetime.now()
for m in mevcut:
    try:
        eklenme = datetime.strptime(m.get("added", bugun.strftime("%Y-%m-%d")), "%Y-%m-%d")
        if (bugun - eklenme).days > 15:
            m["status"] = "past"
    except:
        pass

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

for q in SORGULAR:
    enc = urllib.parse.quote(q)
    url = "https://html.duckduckgo.com/html/?q=" + enc
    req = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")
        sonuclar = re.findall(r'class="result__a"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</a>', html, re.S)
        for raw_baslik, raw_ozet in sonuclar[:15]:
            baslik = re.sub('<[^<]+?>', '', raw_baslik).strip()
            ozet = re.sub('<[^<]+?>', '', raw_ozet).strip()
            metin = (baslik + " " + ozet).lower()

            bulunan_il = None
            for il in ILLER:
                if il.lower() in metin:
                    bulunan_il = il
                    break
            if not bulunan_il:
                continue

            temiz_baslik = baslik[:115]
            if not any(x["title"] == temiz_baslik for x in mevcut):
                mevcut.insert(0, {
                    "city": bulunan_il,
                    "district": "Merkez",
                    "type": "Yapım",
                    "status": "active",
                    "title": temiz_baslik,
                    "org": "EKAP / Kamu İhale Duyurusu",
                    "desc": ozet[:240] + "...",
                    "date": bugun.strftime("%d.%m.%Y"),
                    "added": bugun.strftime("%Y-%m-%d")
                })
    except Exception as e:
        print("Arama hatasi:", e)

print("Toplam kayit:", len(mevcut))
with open("ihaleler.json", "w", encoding="utf-8") as f:
    json.dump(mevcut[:400], f, ensure_ascii=False, indent=2)
