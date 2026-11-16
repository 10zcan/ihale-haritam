import json, urllib.request, xml.etree.ElementTree as ET, re
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

KELIMELER = ["iş makinesi", "ekskavatör", "greyder", "beko loder", "loder", "hafriyat", "kazı", "dozer", "silindir", "kamyon kiralama"]

try:
    with open("ihaleler.json", "r", encoding="utf-8") as f:
        mevcut = json.load(f)
except:
    mevcut = []

url = "https://ilan.gov.tr"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    xml_data = urllib.request.urlopen(req, timeout=20).read()
    root = ET.fromstring(xml_data)
    for item in root.findall(".//item"):
        baslik = item.find("title").text or ""
        aciklama = re.sub('<[^<]+?>', '', item.find("description").text or "")
        tarih = item.find("pubDate").text or datetime.now().strftime("%d.%m.%Y")
        metin = (baslik + " " + aciklama).lower()
        if any(k in metin for k in KELIMELER):
            il_adi = "Ankara"
            for il in ILLER:
                if il.lower() in metin:
                    il_adi = il
                    break
            tur = "Hizmet" if ("kiralama" in metin or "çalıştırılması" in metin) else "Yapım"
            if not any(x["title"] == baslik[:110] for x in mevcut):
                mevcut.insert(0, {
                    "city": il_adi, "district": "Merkez", "type": tur, "status": "active",
                    "title": baslik[:110], "org": "Kamu İhale İlanı",
                    "desc": aciklama[:220] + "...", "date": tarih[:16]
                })
except Exception as e:
    print("Hata:", e)

with open("ihaleler.json", "w", encoding="utf-8") as f:
    json.dump(mevcut[:300], f, ensure_ascii=False, indent=2)
