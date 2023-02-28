from vk_api.longpoll import VkLongPoll, VkEventType
from database import (
    save_user_info_to_bd,
    save_user_and_match_id,
)
from bot_dip import (
    get_top_photos,
    send_some_msg,
    get_user_personal_data,
    has_all_personal_info,
    get_params_for_search,
    search_matched_users,
    should_show_match_to_user,
    get_photo_of_found_person,
    get_city_id_by_name,
    vk_session,
)

longpool = VkLongPoll(vk_session)

for event in longpool.listen():
    current_state = "idle"
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id
            if msg == "match":
                user_data = get_user_personal_data(id)
                print(user_data)
                has_all_info = has_all_personal_info(user_data)
                if not has_all_info:
                    send_some_msg(
                        id,
                        "Напишите данные в виде: #Возраст, город проживания, пол, семейное положение.",
                    )
                    continue
                search_params = get_params_for_search(user_data)
                for match in search_matched_users(*search_params):
                    if should_show_match_to_user(id, match):
                        print(match)
                        user_photo = get_photo_of_found_person(match["id"])
                        top_photos = get_top_photos(user_photo)
                        attachment = [
                            f'photo{match["id"]}_{photo["id"]}' for photo in top_photos
                        ]
                        attachment_string = ",".join(attachment)
                        vk_link = f'vk.com/id{match["id"]}'
                        send_some_msg(
                            id,
                            f"{vk_link} \nВот лучшие фотографии: ",
                            attachment_string,
                        )
                        save_user_and_match_id(id, match["id"])
                        break
            elif msg.startswith("#"):
                message1 = msg[1:]
                age, city, sex, relation = message1.split(", ")
                city = get_city_id_by_name(city)
                save_user_info_to_bd(id, age, city, sex, relation)
                send_some_msg(id, "Информация записана в базу данных.")
            else:
                send_some_msg(id, 'Для получения совпадений напишите слово "match"')
