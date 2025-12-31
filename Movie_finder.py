"""
MovieGraphPy - Neo4j Movies Veri Seti ile Python Uygulaması
Kocaeli Sağlık ve Teknoloji Üniversitesi
Programlama Lab 1 - Proje 3
"""

from neo4j import GraphDatabase
import json
import os

# ==================== NEO4J BAĞLANTI AYARLARI ====================
URI = "bolt://YENI_IP_ADRESI:7687"
USERNAME = "neo4j"
PASSWORD = "YENI_SIFRE"

# ==================== GLOBAL DEĞİŞKENLER ====================
driver = None
secili_film = None  # Son aranan/seçilen film bilgisi
arama_sonuclari = []  # Son arama sonuçları


# ==================== VERİTABANI FONKSİYONLARI ====================

def veritabanina_baglan():
    """Neo4j veritabanına bağlantı kurar."""
    global driver
    try:
        driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        # Bağlantıyı test et
        driver.verify_connectivity()
        print("[OK] Neo4j veritabanina basariyla baglanildi!")
        return True
    except Exception as e:
        print(f"[HATA] Neo4j baglantisi kurulamadi: {e}")
        return False


def baglanti_kapat():
    """Veritabanı bağlantısını kapatır."""
    global driver
    if driver:
        driver.close()
        print("Veritabanı bağlantısı kapatıldı.")


# ==================== FİLM ARAMA FONKSİYONU ====================

def film_ara(anahtar_kelime):
    """
    Film adına göre arama yapar (kısmi eşleşme).
    Sonuçları numaralı liste olarak döndürür.
    """
    global arama_sonuclari
    
    if not anahtar_kelime or anahtar_kelime.strip() == "":
        print("\n[UYARI] Bos arama yapilamaz! Lutfen bir film adi girin.")
        return []
    
    query = """
    MATCH (m:Movie)
    WHERE toLower(m.title) CONTAINS toLower($anahtar)
    RETURN m.title AS title, m.released AS released
    ORDER BY m.released DESC
    """
    
    try:
        with driver.session() as session:
            result = session.run(query, anahtar=anahtar_kelime.strip())
            arama_sonuclari = []
            
            for record in result:
                arama_sonuclari.append({
                    "title": record["title"],
                    "released": record["released"]
                })
            
            if not arama_sonuclari:
                print(f"\n[HATA] '{anahtar_kelime}' icin sonuc bulunamadi.")
                return []
            
            print(f"\n{'='*50}")
            print(f"  '{anahtar_kelime}' için {len(arama_sonuclari)} sonuç bulundu:")
            print(f"{'='*50}")
            
            for i, film in enumerate(arama_sonuclari, 1):
                yil = film["released"] if film["released"] else "?"
                print(f"  {i}) {film['title']} ({yil})")
            
            print(f"{'='*50}")
            return arama_sonuclari
            
    except Exception as e:
        print(f"\n[HATA] Arama sirasinda hata olustu: {e}")
        return []


# ==================== FİLM DETAY FONKSİYONU ====================

def film_detay_goster(film_index):
    """
    Seçilen filmin detaylarını gösterir:
    - Film adı, yıl, tagline
    - Yönetmen(ler)
    - Oyuncular (en az 5 kişi)
    """
    global secili_film, arama_sonuclari
    
    # Geçerli index kontrolü
    if not arama_sonuclari:
        print("\n[UYARI] Once film aramasi yapmalisiniz!")
        return None
    
    try:
        index = int(film_index) - 1
        if index < 0 or index >= len(arama_sonuclari):
            print(f"\n[UYARI] Gecersiz numara! 1-{len(arama_sonuclari)} arasinda bir sayi girin.")
            return None
    except ValueError:
        print("\n[UYARI] Lutfen gecerli bir sayi girin!")
        return None
    
    film_adi = arama_sonuclari[index]["title"]
    
    # Film detaylarını çek
    query = """
    MATCH (m:Movie {title: $title})
    OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
    OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
    RETURN m.title AS title, 
           m.released AS released, 
           m.tagline AS tagline,
           collect(DISTINCT d.name) AS directors,
           collect(DISTINCT a.name) AS actors
    """
    
    try:
        with driver.session() as session:
            result = session.run(query, title=film_adi)
            record = result.single()
            
            if not record:
                print(f"\n[HATA] '{film_adi}' filmi bulunamadi!")
                return None
            
            # Sonuçları işle
            title = record["title"]
            released = record["released"] if record["released"] else "Bilinmiyor"
            tagline = record["tagline"] if record["tagline"] else "Tagline yok"
            directors = record["directors"] if record["directors"] else []
            actors = record["actors"] if record["actors"] else []
            
            # Boş değerleri filtrele
            directors = [d for d in directors if d]
            actors = [a for a in actors if a]
            
            # Seçili filmi kaydet (graph.json için)
            secili_film = {
                "title": title,
                "released": released,
                "tagline": tagline,
                "directors": directors,
                "actors": actors
            }
            
            # Ekrana yazdır
            print(f"\n{'='*60}")
            print(f"  FILM DETAYLARI")
            print(f"{'='*60}")
            print(f"  Film Adı  : {title}")
            print(f"  Yıl       : {released}")
            print(f"  Tagline   : {tagline}")
            print(f"{'='*60}")
            
            print(f"\n  YONETMEN(LER):")
            if directors:
                for director in directors:
                    print(f"     • {director}")
            else:
                print("     (Yönetmen bilgisi bulunamadı)")
            
            print(f"\n  OYUNCULAR (Ilk 5):")
            if actors:
                for actor in actors[:5]:  # En az 5 kişi göster
                    print(f"     • {actor}")
                if len(actors) > 5:
                    print(f"     ... ve {len(actors) - 5} oyuncu daha")
            else:
                print("     (Oyuncu bilgisi bulunamadı)")
            
            print(f"\n{'='*60}")
            
            return secili_film
            
    except Exception as e:
        print(f"\n[HATA] Film detaylari alinirken hata olustu: {e}")
        return None


# ==================== GRAPH.JSON OLUŞTURMA ====================

def graph_json_olustur():
    """
    Seçili film için graph.json dosyası oluşturur.
    Format:
    - nodes: Movie ve Person düğümleri
    - links: ACTED_IN ve DIRECTED bağlantıları
    """
    global secili_film
    
    if not secili_film:
        print("\n[UYARI] Once bir film secmelisiniz! (Film Detayi Goster)")
        return False
    
    film_adi = secili_film["title"]
    
    # Graf verilerini çek
    query = """
    MATCH (m:Movie {title: $title})
    OPTIONAL MATCH (m)<-[r:DIRECTED|ACTED_IN]-(p:Person)
    RETURN m, p, type(r) AS relationship_type
    """
    
    try:
        with driver.session() as session:
            result = session.run(query, title=film_adi)
            
            nodes = []
            links = []
            node_ids = set()
            
            # Film düğümünü ekle
            film_node_id = f"movie_{film_adi.replace(' ', '_')}"
            nodes.append({
                "id": film_node_id,
                "label": film_adi,
                "type": "Movie",
                "released": secili_film["released"],
                "tagline": secili_film["tagline"]
            })
            node_ids.add(film_node_id)
            
            # Kişileri ve ilişkileri ekle
            for record in result:
                person = record["p"]
                rel_type = record["relationship_type"]
                
                if person and rel_type:
                    person_name = person["name"]
                    person_node_id = f"person_{person_name.replace(' ', '_')}"
                    
                    # Kişi düğümünü ekle (tekrar etmemesi için kontrol)
                    if person_node_id not in node_ids:
                        nodes.append({
                            "id": person_node_id,
                            "label": person_name,
                            "type": "Person"
                        })
                        node_ids.add(person_node_id)
                    
                    # İlişkiyi ekle
                    links.append({
                        "source": person_node_id,
                        "target": film_node_id,
                        "type": rel_type
                    })
            
            # JSON yapısını oluştur
            graph_data = {
                "nodes": nodes,
                "links": links
            }
            
            # exports klasörünü oluştur
            exports_dir = os.path.join(os.path.dirname(__file__), "exports")
            if not os.path.exists(exports_dir):
                os.makedirs(exports_dir)
            
            # graph.json dosyasını yaz
            json_path = os.path.join(exports_dir, "graph.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n{'='*60}")
            print(f"  [OK] graph.json basariyla olusturuldu!")
            print(f"{'='*60}")
            print(f"  Dosya: exports/graph.json")
            print(f"  Film : {film_adi}")
            print(f"  Düğüm Sayısı: {len(nodes)}")
            print(f"  Bağlantı Sayısı: {len(links)}")
            print(f"{'='*60}")
            
            return True
            
    except Exception as e:
        print(f"\n[HATA] graph.json olusturulurken hata olustu: {e}")
        return False


# ==================== ANA MENÜ ====================

def menu_goster():
    """Ana menüyü gösterir."""
    print(f"\n{'='*50}")
    print("  MovieGraphPy - Film Arama Uygulamasi")
    print(f"{'='*50}")
    print("  1. Film Ara")
    print("  2. Film Detayı Göster")
    print("  3. Seçili Film için graph.json Oluştur")
    print("  4. Çıkış")
    print(f"{'='*50}")


def ana_dongu():
    """Ana program döngüsü."""
    while True:
        menu_goster()
        
        try:
            secim = input("  Seçiminiz (1-4): ").strip()
        except KeyboardInterrupt:
            print("\n\nProgram sonlandırıldı.")
            break
        
        if secim == "1":
            # Film Ara
            anahtar = input("\n  Aranacak film adı: ").strip()
            film_ara(anahtar)
            
        elif secim == "2":
            # Film Detayı Göster
            if not arama_sonuclari:
                print("\n[UYARI] Once film aramasi yapmalisiniz!")
            else:
                numara = input("\n  Film numarası seçin: ").strip()
                film_detay_goster(numara)
                
        elif secim == "3":
            # Graph.json Oluştur
            graph_json_olustur()
            
        elif secim == "4":
            # Çıkış
            print("\n  Gule gule!")
            break
            
        else:
            print("\n[UYARI] Gecersiz secim! Lutfen 1-4 arasinda bir sayi girin.")
        
        # Devam etmek için Enter bekle
        input("\n  Devam etmek için Enter'a basın...")


# ==================== PROGRAM GİRİŞ NOKTASI ====================

def main():
    """Ana fonksiyon."""
    print("\n" + "="*60)
    print("  MovieGraphPy - Neo4j Film Arama Uygulamasi")
    print("  Kocaeli Sağlık ve Teknoloji Üniversitesi")
    print("  Programlama Lab 1 - Proje 3")
    print("="*60)
    
    # Veritabanına bağlan
    if not veritabanina_baglan():
        print("\n[HATA] Program sonlandiriliyor. Baglanti ayarlarini kontrol edin.")
        return
    
    try:
        # Ana döngüyü başlat
        ana_dongu()
    finally:
        # Bağlantıyı kapat
        baglanti_kapat()


if __name__ == "__main__":
    main()
