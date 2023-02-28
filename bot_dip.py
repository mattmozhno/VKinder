import vk_api
from database import (
    save_user_info_to_bd,
    is_already_matched,
    get_user_info_from_bd,
    create_db,
    create_matches_table,
    create_user_info_table,
)

from config import user_token, bot_token
from datetime import datetime

vk_session = vk_api.VkApi(token=bot_token)
session_api = vk_session.get_api()

create_db()
create_user_info_table()
create_matches_table()

vk_user_session = vk_api.VkApi(token=user_token)
vk_user_api = vk_user_session.get_api()
vk_user_session._auth_token()


def send_some_msg(id, some_text, attachment=""):
    session_api.messages.send(
        user_id=id, message=some_text, attachment=attachment, random_id=0
    )


def get_user_personal_data(user_id):
    user_data = get_user_info_from_bd(user_id)
    if user_data:
        return user_data
    result = vk_session.method(
        "users.get", {"user_ids": str(user_id), "fields": "bdate, city, sex, relation"}
    )[0]
    try:
        bdate = datetime.strptime(result["bdate"], "%d.%m.%Y")
    except ValueError:
        bdate = None
    if bdate:
        today_date = datetime.today()
        age = today_date.year - bdate.year
    else:
        age = None
    city = result.get("city", {}).get("id")
    sex = result.get("sex")
    relation = result.get("relation", 1)
    save_user_info_to_bd(user_id, age, city, sex, relation)
    return {"city": city, "age": age, "sex": sex, "relation": relation}


def get_params_for_search(user_data):
    city_id = user_data["city"]
    age_from = user_data["age"] - 5
    age_to = user_data["age"] + 5
    sex = 1 if user_data["sex"] == 2 else 2
    relation = 1
    return (age_from, age_to, city_id, sex, relation)


def get_city_id_by_name(city_name):
    result = vk_user_api.database.getCities(q=city_name, need_all=0, count=1)
    return result["items"][0]["id"]


def search_matched_users(age_from, age_to, city_id, sex, relation):
    result = vk_user_session.method(
        "users.search",
        {
            "city": city_id,
            "age_from": age_from,
            "age_to": age_to,
            "sex": sex,
            "status": relation,
            "count": 100,
        },
    )
    return result["items"]


def has_all_personal_info(user_data):
    required_fields = {"age", "city", "sex", "relation"}
    if set(user_data.keys()) == required_fields:
        return True
    else:
        return False


def should_show_match_to_user(user_id, match_dict):
    if not match_dict["is_closed"] and not is_already_matched(
        user_id, match_dict["id"]
    ):
        return True
    return False


def get_photo_of_found_person(user_id):
    """getting a photo of a found person"""
    res = vk_user_api.photos.get(
        owner_id=user_id, album_id="profile", extended=1, count=30
    )
    return res


def get_rating(photo):
    return photo["rating"]


def get_top_photos(all_photos):
    good_pictures = []
    for photo in all_photos["items"]:
        good_picture = {}
        good_picture["url"] = photo["sizes"][-1]["url"]
        good_picture["likes"] = photo["likes"]["count"]
        good_picture["comments"] = photo["comments"]["count"]
        good_picture["rating"] = good_picture["likes"] + good_picture["comments"]
        good_picture["id"] = photo["id"]
        good_picture["owner_id"] = photo["owner_id"]
        good_pictures.append(good_picture)
    good_pictures.sort(key=get_rating, reverse=True)
    return good_pictures[0:3]
