import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Artist, Museum, Painting
from app import models

def seed_database():
    db = SessionLocal()
    
    try:
        with db.begin():
            artists = [
            Artist(
                artist_short_name="Гончарова Н.С.",
                artist_long_name="Гончарова Наталья Сергеевна",
                dob="1881-07-03",
                dob_place="д.Нагаево Тульской губ",
                dod="1962-10-17", 
                dod_place="Париж"
            ),
            Artist(
                artist_short_name="Родченко А.М.",
                artist_long_name="Родченко Александр Михайлович", 
                dob="1891-12-05",
                dob_place="Санкт-Петербург",
                dod="1956-12-03",
                dod_place="Москва"
            ),
            Artist(
                artist_short_name="Удальцова Н.А.",
                artist_long_name="Удальцова Надежда Андреевна",
                dob="1885-12-29", 
                dob_place="Орёл",
                dod="1961-01-25",
                dod_place="Москва"
            )
        ]
        
            museums = [
            Museum(
                name="Государственный Русский музей",
                name_unique="russian_museum",
                contact="+7-812-123-45-67",
                profile="20241107110255-46184df43c05ab8634927f8848667b5ca7-russian-museum.rvertical.w1200.webp",
                profile_path="https://art-api.srvdev.ru/storage/app/museum-images/20241107110255-46184df43c05ab8634927f8848667b5ca7-russian-museum.rvertical.w1200.webp",
                city="Санкт-Петербург",
                state="Санкт-Петербург",
                country="Россия",
                country_code=7,
                zipcode=191186,
                website="https://rusmuseum.ru"
            ),
            Museum(
                name="Государственная Третьяковская галерея",
                name_unique="tretyakov_gallery",
                contact="+7-495-123-45-67", 
                profile="tretyakov-gallery.webp",
                profile_path="https://art-api.srvdev.ru/storage/app/museum-images/tretyakov-gallery.webp",
                city="Москва",
                state="Москва",
                country="Россия",
                country_code=7,
                zipcode=119017,
                website="https://tretyakovgallery.ru"
            )
        ]
        
            db.add_all(artists)
            db.add_all(museums)
            db.flush()
        
            paintings = [
            Painting(
                title="Велосипедист",
                unique_title="cyclist_1913",
                type="живопись",
                genre="Бытовой",
                materials=["холст", "масло"],
                size="75 на 105",
                profile="20241212125949-cyclist_1913.webp",
                profile_path="https://art-api.srvdev.ru/storage/app/painting-images/20241212125949-cyclist_1913.webp",
                year=1913,
                period="Конец XIX - начало XX века",
                style=["кубофутуризм", "авангард"],
                artist_id=artists[0].id,
                museum_id=museums[0].id
            ),
            Painting(
                title="Черное на черном",
                unique_title="black_on_black_1918", 
                type="живопись",
                genre="Абстрактный",
                materials=["холст", "масло"],
                size="80 на 60",
                profile="black_on_black_1918.webp",
                profile_path="https://art-api.srvdev.ru/storage/app/painting-images/black_on_black_1918.webp",
                year=1918,
                period="Русский авангард", 
                style=["супрематизм", "конструктивизм"],
                artist_id=artists[1].id,
                museum_id=museums[1].id
            ),
            Painting(
                title="Ресторан",
                unique_title="restaurant_1915",
                type="живопись", 
                genre="Городской пейзаж",
                materials=["холст", "масло"],
                size="65 на 81",
                profile="restaurant_1915.webp",
                profile_path="https://art-api.srvdev.ru/storage/app/painting-images/restaurant_1915.webp",
                year=1915,
                period="Русский авангард",
                style=["кубизм", "футуризм"],
                artist_id=artists[2].id,
                museum_id=museums[0].id
            )
        ]
        
            db.add_all(paintings)
        
        print("✅ База данных успешно заполнена!")
        print("🎨 Добавлено:")
        print(f"   - Художников: {len(artists)}")
        print(f"   - Музеев: {len(museums)}") 
        print(f"   - Картин: {len(paintings)}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()