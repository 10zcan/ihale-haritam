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
    "kanalizasyon yapım işi ihale",
    "içme suyu altyapı yapım ihalesi",
    "doğalgaz elektrik altyapı kazı ihale",
    "dere ıslahı hafriyat yol yapım ihalesi"
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

for q in SORGULAR:
    encoded = urllib.parse.quote(q)
    url = "https://google.com" + encoded + "&hl=tr&gl=TR&ceid=TR:tr"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        xml_data = urllib.request.urlopen(req, timeout=20).read()
        root = ET.fromstring(xml_data)
        for item in root.findall(".//item")[:25]:
            baslik = item.find("title").text or ""
            aciklama = re.sub('<[^<]+?>', '', item.find("description").text or "")
            pub = item.find("pubDate").text or ""
            metin = (baslik + " " + aciklama).lower()

            bulunan_il = None
            for il in ILLER:
                if il.lower() in metin:
                    bulunan_il = il
                    break
            if not bulunan_il:
                continue
            temiz_baslik = baslik[:115]
            kaynak = "EKAP / Kamu İhale"
            

            if not any(x["title"] == temiz_baslik for x in mevcut):
                mevcut.insert(0, {
                    "city": bulunan_il,
                    "district": "Merkez",
                    "type": "Yapım",
                    "status": "active",
                    "title": temiz_baslik,
                    "org": kaynak,
                    "desc": aciklama[:240] + "...",
                    "date": pub[:16],
                    "added": bugun.strftime("%Y-%m-%d")
                })
    except Exception as e:
        print("Sorgu hatasi:", e)

with open("ihaleler.json", "w", encoding="utf-8") as f:
    json.dump(mevcut[:400], f, ensure_ascii=False, indent=2)
                
