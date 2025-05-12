import re
import time
from datetime import datetime

import scrapy
from scrapy.http import Response

from selenium import webdriver
from selenium.webdriver.common.by import By

from db.engine import SessionLocal
from db.models import Auto, kyiv_tz


class AutoSpider(scrapy.Spider):
    name = "auto"
    allowed_domains = ["auto.ria.com"]
    start_urls = ["https://auto.ria.com/uk/car/used/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Remote(
            command_executor="http://selenium:4444/wd/hub",
            options=options
        )

    def close(self, reason: str) -> None:
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Ошибка при закрытии драйвера: {e}")
            self.driver = None

    def parse(self, response: Response, **kwargs):
        for auto_url in response.css("a.photo-185x120::attr(href)").getall():
            yield response.follow(auto_url, callback=self.parse_auto)
        next_page = response.css("span.page-item.next.text-r a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_auto(self, response: Response, **kwargs):
        def safe_css(selector, strip=True, default=''):
            value = response.css(selector).get(default=default)
            return value.strip() if value and strip else value

        username = (
            safe_css("div.seller_info_name.bold > a::text") or
            safe_css("div.seller_info_name.bold::text") or
            safe_css("h4.seller_info_name > a::text")
        )

        images_count_raw = safe_css("span.count > span.mhide::text", strip=True)
        images_count = int(images_count_raw.replace("з ", "")) if images_count_raw else None

        car_number = safe_css("span.state-num.ua::text")
        car_vin = "".join(
            v.strip() for v in response.css("div.t-check span.label-vin::text").getall() if v.strip()
        ) or safe_css("span.vin-code::text")

        title = safe_css("h1.head::text")
        url = response.url

        price_usd = self.extract_price(response)
        odometer = safe_css("div.base-information.bold > span::text")
        if odometer:
            odometer = int(odometer.replace(" ", "")) * 1000

        image_url = response.css("div.carousel-inner picture img::attr(src)").get()
        phone_number = self.click_number(response)

        # Database interaction
        session = SessionLocal()
        try:
            existing_auto = session.query(Auto).filter_by(url=url).first()
            now = datetime.now(kyiv_tz)

            if existing_auto:
                # Update
                existing_auto.title = title
                existing_auto.price_usd = price_usd
                existing_auto.odometer = odometer
                existing_auto.username = username
                existing_auto.phone_number = phone_number
                existing_auto.image_url = image_url
                existing_auto.images_count = images_count
                existing_auto.car_number = car_number
                existing_auto.car_vin = car_vin
                existing_auto.datetime_found = now
                self.logger.info(f"🔁 Обновлено: {url}")
            else:
                # Create
                new_auto = Auto(
                    title=title,
                    url=url,
                    price_usd=price_usd,
                    odometer=odometer,
                    username=username,
                    image_url=image_url,
                    images_count=images_count,
                    car_number=car_number,
                    car_vin=car_vin,
                    phone_number=phone_number,
                    datetime_found=now
                )
                session.add(new_auto)

            session.commit()
            self.logger.info(f"✅ Сохранено авто: {title} | {url}")

        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения авто: {e}")
            session.rollback()
        finally:
            session.close()

        yield {
            "title": title,
            "url": url,
            "price_usd": price_usd,
            "odometer": odometer,
            "username": username,
            "image_url": image_url,
            "images_count": images_count,
            "car_number": car_number,
            "car_vin": car_vin,
            "phone_number": phone_number,
        }

    def extract_price(self, response: Response):
        price_raw = response.css("div.price_value > strong::text").get()
        if not price_raw or "грн" in price_raw or "€" in price_raw:
            price_raw = response.css("div.price_value--additional > span > span::text").get()

        price_clean = re.sub(r'\D', '', price_raw or "")
        try:
            return float(price_clean) if price_clean else None
        except ValueError:
            return None

    def click_number(self, response: Response):
        try:
            self.driver.get(response.url)
            time.sleep(2)

            # Закрыть уведомление, если появилось
            try:
                notif_button = self.driver.find_element(By.CSS_SELECTOR, "div.c-notifier-start a")
                notif_button.click()
            except:
                pass

            time.sleep(1)

            try:
                phone_button = self.driver.find_element(By.CSS_SELECTOR, "section.seller div.phones_item span.phone.bold a")
                phone_button.click()
            except:
                try:
                    phone_button = self.driver.find_element(By.CSS_SELECTOR, "section.seller div.phones_list div.phones_item span.phone.bold a")
                    phone_button.click()
                except:
                    pass

            time.sleep(2)
            phone_div = self.driver.find_element(By.CSS_SELECTOR, "div.popup-successful-call-desk")
            return phone_div.text.strip()
        except Exception as e:
            self.logger.warning(f"❌ Не удалось получить номер телефона: {e}")
            return None
