import time
import logging

import requests
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    ElementNotInteractableException,
)

from bs4 import BeautifulSoup

from yandex_parcer.utils.consts import *
from yandex_parcer.file_manager import save_cache_responce, get_cache_responce


def scroll_window(driver, max_scroll=500):
    # Прокручиваем организации вниз до конца
    slider = driver.find_element_by_class_name(name=SCROLLBAR_THUMB)
    for i in range(max_scroll):
        try:
            (
                ActionChains(driver)
                .click_and_hold(slider)
                .move_by_offset(0, max(100 - i * 2, 5))
                .release()
                .perform()
            )
            time.sleep(1)
        except MoveTargetOutOfBoundsException:
            break
        except ElementNotInteractableException:
            break
    logging.info(f"Прокрутили страницу {i} раз")


def get_organizations_by_link(link):
    href = get_cache_responce(link, ORGANIZATION_LINKS_FILE_NAME)
    if href:
        logging.info(f"Получено {len(href)} ссылок на организации из кэша")
        return href

    driver = webdriver.Safari()
    driver.maximize_window()
    try:
        # Заходим на страницу
        driver.get(link)
        time.sleep(3)
        logging.info("Начинаем скролл организаций")
        scroll_window(driver, max_scroll=25)

        # Получаем ссылки на организации
        organizations = driver.find_elements_by_class_name(name=ORGANIZATION)
        organizations_href = []
        for organization in organizations:
            try:
                organizations_href.append(organization.get_attribute("href"))
            except Exception as e:
                logging.error(f"Не удалось получить ссылку на организацию: {e}")
                continue
    finally:
        driver.quit()
    logging.info(f"Получено {len(organizations_href)} ссылок на организации")
    save_cache_responce(link, organizations_href, ORGANIZATION_LINKS_FILE_NAME)
    return organizations_href


def get_organization_info_by_link(organizations_link: list[str]):
    driver = webdriver.Safari()
    driver.maximize_window()
    logging.info(f"Получаем информацию о {len(organizations_link)} организациях")
    try:
        for link in tqdm(organizations_link):
            try:
                info = get_cache_responce(link, ORGANIZATION_INFO_FILE_NAME)
                if info:
                    continue
                # Получаем основную инфу
                driver.get(link)
                time.sleep(5)
                page = driver.page_source
                info = parce_main_organization_page(page)
                info["longitude"], info["latitude"] = get_coordinates(
                    driver.current_url
                )
                info.update(get_district_name(info["latitude"], info["longitude"]))
                # Получаем отзывы
                review_link = link + "reviews"
                driver.get(review_link)
                time.sleep(3)
                max_scroll = min(500, int(info.get("n_reviews", 0)) // 8) + 1
                # scroll_window(driver, max_scroll)

                info.update(parce_reviews_page(driver.page_source))
                save_cache_responce(link, info, ORGANIZATION_INFO_FILE_NAME)
            except Exception as e:
                logging.error(
                    f"Не удалось получить информацию о организации: {link}\n{e}"
                )
                continue
    finally:
        driver.quit()
    logging.info(f"Получена информация о {len(organizations_link)} организациях")


def parce_main_organization_page(page):
    soup = BeautifulSoup(page, "lxml")
    info = {}

    info["name"] = get_page_attribute(soup, "h1", ORGANIZATION_NAME)
    info["address"] = get_page_attribute(soup, "a", ORGANIZATION_ADDRESS)
    info["open_hours"] = get_open_hours(soup)
    info["n_reviews"] = get_page_attribute(
        soup, "div", ORGANIZATION_REVIEWS_COUNT
    ).split()[0]
    try:
        info["n_reviews"] = int(info["n_reviews"])
    except ValueError:
        info["n_reviews"] = 0
    info["rating"] = get_rating(soup)
    return info


def get_coordinates(link):
    coordinates = link.split("/")[-1]
    coordinates = coordinates.replace("?ll=", "").split("&")[0].split("%2C")
    return coordinates


def get_page_attribute(
    soup, element, class_name, style_attribute="class", attribute="text"
):
    try:
        if attribute == "text":
            return soup.find(element, {style_attribute: class_name}).text
        return soup.find(element, {style_attribute: class_name}).get(attribute)
    except AttributeError:
        return ""


def get_open_hours(soup):
    opening_hours = []
    for data in soup.find_all("meta", {"itemprop": ORGANIZATION_OPENING_HOURS}):
        if data.get("content") == "Mo 08:00-23:00":
            continue
        opening_hours.append(data.get("content"))

    days = ["mo", "tu", "we", "th", "fr", "sa", "su"]
    opening_hours_new = {}.fromkeys(days, "weekend")
    for day in opening_hours:
        day_name = day[:2].lower()
        work_time = day[3:]
        opening_hours_new[day_name] = work_time
    return opening_hours_new


def get_rating(soup):
    stars_div = soup.find("div", {"class": ORGANIZATION_STARS})
    if not stars_div:
        return 0
    star_full = len(stars_div.find_all("span", {"class": STAR_FULL}))
    star_half = len(stars_div.find_all("span", {"class": STAR_HALF})) * 0.5
    return star_full + star_half


def parce_reviews_page(page):
    soup = BeautifulSoup(page, "lxml")
    info = {}
    info["topics_rating"], info["topics_count"] = get_topics_info(soup)
    info["reviews"] = get_reviews(soup)
    return info


def get_reaction(soup):
    reactions = soup.find_all("div", {"class": REVIEW_REACTION})
    like, dislike = reactions[0].text, reactions[1].text
    return like, dislike


def get_topics_info(soup):
    topics = {}
    topics_count = {}
    for topic in soup.find_all("div", {"class": TOPIC_CASE}):
        name, rating = get_page_attribute(topic, "div", TOPIC_NAME).split(" • ")
        count = get_page_attribute(topic, "div", TOPIC_COUNT).split()[0]
        topics[name] = rating.replace("%", "")
        topics_count[name] = count
    return topics, topics_count


def get_reviews(soup):
    reviews = []

    for review in soup.find_all("div", {"class": REVIEW}):
        review_info = {}
        review_info["text"] = get_page_attribute(review, "span", REVIEW_TEXT)
        review_info["date"] = get_page_attribute(
            review, "meta", REVIEW_DATE, "itemprop", "content"
        )
        review_info["name"] = get_page_attribute(
            review, "span", REVIEW_NAME, "itemprop"
        )
        review_info["rating"] = get_rating(review)
        review_info["like"], review_info["dislike"] = get_reaction(review)
        reviews.append(review_info)

    return reviews


def get_district_name(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    response = requests.get(url)
    location_dict = {}

    if response.status_code == 200:
        data = response.json()
        address = data.get("address", {})
        location_dict["district"] = address.get(
            "city_district", ""
        )  # You can use other keys like "city", "state", "suburb", etc. as needed.
        location_dict["state"] = address.get("state", "")
        location_dict["region"] = address.get("region", "")

        return location_dict
    else:
        return None
