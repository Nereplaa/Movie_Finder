# MovieGraphPy

Neo4j Movies veri seti ile calisan Python film arama uygulamasi.

> **Kocaeli Saglik ve Teknoloji Universitesi**  
> Programlama Lab 1 - Proje 3

## Proje Hakkinda

Bu uygulama, Neo4j graf veritabanina baglanarak film arama, detay goruntuleme ve graf verisi uretme islemlerini gerceklestirir.

### Ozellikler

- **Film Arama** - Kismi eslesme ile film bulma
- **Detay Gosterme** - Yonetmen, oyuncular ve film bilgileri
- **Graf Ciktisi** - JSON formatinda iliskisel veri uretme
- **Hata Yonetimi** - Kullanici dostu hata mesajlari

## Teknolojiler

| Teknoloji | Versiyon | Kullanim |
|-----------|----------|----------|
| Python | 3.x | Ana programlama dili |
| Neo4j | 5.x | Graf veritabani |
| neo4j-driver | 5.x | Python-Neo4j baglantisi |

## Kurulum

### 1. Gerekli Kutuphanevi Yukleyin

```bash
pip install neo4j
```

### 2. Neo4j Baglanti Ayarlari

`Movie_finder.py` dosyasindaki baglanti bilgilerini guncelleyin:

```python
URI = "bolt://localhost:7687"      # Neo4j sunucu adresi
USERNAME = "neo4j"                  # Kullanici adi
PASSWORD = "your_password"          # Sifre
```

### 3. Programi Calistirin

```bash
python Movie_finder.py
```

## Kullanim

Program acildiginda CLI menusu goruntulenir:

```
==================================================
  MovieGraphPy - Film Arama Uygulamasi
==================================================
  1. Film Ara
  2. Film Detayi Goster
  3. Secili Film icin graph.json Olustur
  4. Cikis
==================================================
```

### Film Arama

```
Aranacak film adi: Matrix

==================================================
  'Matrix' icin 3 sonuc bulundu:
==================================================
  1) The Matrix Revolutions (2003)
  2) The Matrix Reloaded (2003)
  3) The Matrix (1999)
==================================================
```

### Film Detayi

```
Film numarasi secin: 3

============================================================
  FILM DETAYLARI
============================================================
  Film Adi  : The Matrix
  Yil       : 1999
  Tagline   : Welcome to the Real World
============================================================

  YONETMEN(LER):
     - Lana Wachowski
     - Lilly Wachowski

  OYUNCULAR (Ilk 5):
     - Keanu Reeves
     - Carrie-Anne Moss
     - Laurence Fishburne
     - Hugo Weaving
     - Emil Eifrem
```

### Graph.json Ciktisi

Secili film icin `exports/graph.json` dosyasi olusturulur:

```json
{
  "nodes": [
    {"id": "movie_The_Matrix", "label": "The Matrix", "type": "Movie"},
    {"id": "person_Keanu_Reeves", "label": "Keanu Reeves", "type": "Person"}
  ],
  "links": [
    {"source": "person_Keanu_Reeves", "target": "movie_The_Matrix", "type": "ACTED_IN"}
  ]
}
```

## Proje Yapisi

```
Programalama_Lab_III/
├── Movie_finder.py      # Ana uygulama
├── README.md            # Bu dosya
└── exports/
    └── graph.json       # Uretilen graf verisi
```

## Veritabani Semasi

```
(:Movie) <-[:DIRECTED]- (:Person)
(:Movie) <-[:ACTED_IN]- (:Person)
(:Movie) <-[:PRODUCED]- (:Person)
(:Movie) <-[:WROTE]- (:Person)
```

## Cypher Sorgulari

### Film Arama
```cypher
MATCH (m:Movie)
WHERE toLower(m.title) CONTAINS toLower($anahtar)
RETURN m.title, m.released
ORDER BY m.released DESC
```

### Film Detay
```cypher
MATCH (m:Movie {title: $title})
OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
RETURN m.title, m.released, m.tagline,
       collect(DISTINCT d.name) AS directors,
       collect(DISTINCT a.name) AS actors
```

### Graf Verisi
```cypher
MATCH (m:Movie {title: $title})
OPTIONAL MATCH (m)<-[r:DIRECTED|ACTED_IN]-(p:Person)
RETURN m, p, type(r) AS relationship_type
```

## Lisans

Bu proje egitim amacli gelistirilmistir.

---

**Gelistirici:** Alperen  
**Universite:** Kocaeli Saglik ve Teknoloji Universitesi  
**Ders:** Programlama Lab 1  
**Tarih:** 2025
# Movie_Finder
