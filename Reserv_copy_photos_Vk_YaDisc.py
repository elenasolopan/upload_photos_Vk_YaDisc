from pprint import pprint
import requests
from tqdm import tqdm
import json


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.token = token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.user_id = None
        self.album_info = dict()

    def get_id_user(self, login):
        if login.isdigit():
            self.user_id = int(login)
        else:
            user_params = {'screen_name': login}
            res = requests.get(self.url + 'utils.resolveScreenName', params={**self.params, **user_params})
            self.user_id = res.json()['response']['object_id']
        return self.user_id

    def all_albums(self):
        album_params = {'owner_id': self.user_id}
        res = requests.get(self.url + 'photos.getAlbums', params={**self.params, **album_params})
        res = res.json()['response']['items']
        for i in res[0:]:
            self.album_info.update({"стена": 'wall', "аватар": 'profile', i['title']: i['id']})
        print("\nСписок фотоальбомов пользователя: ")
        return list(self.album_info.keys())

    def get_photos(self, album, number):
        data = dict()
        photos_list = []
        if album in self.album_info.keys():
            photos_params = {
                        'user_id': self.user_id,
                        'album_id': self.album_info.values(),
                        'count': number,
                        'extended': '1'
                        }
            res = requests.get(self.url + 'photos.get', params={**self.params, **photos_params})
            res = res.json()['response']['items']
            for i in res[0:]:
                info_photos = dict(
                file_name=f"{i['likes']['count']}_{i['date']}.jpg",
                size=i['sizes'][-1]['type'],
                URL_photo=i['sizes'][-1]['url'])
                photos_list.append(info_photos)
            json_list = []
            for j in photos_list:
                json_list.append({"file_name": j['file_name'], "size": j['size']})
            data[album] = json_list
            with open("info_photos.json", 'w', encoding='utf-8')as f:
                json.dump(data, f, ensure_ascii=False)
            return photos_list



vk_client = VkUser(input("Введите токен пользователя Vk: "), '5.130')
pprint(vk_client.get_id_user(input("Введите id или логин пользователя Vk: ")))
pprint(vk_client.all_albums())
photos = vk_client.get_photos(str(input("\nВыберите папку с фото для загрузки: ")), int(input("Введите колличество фотографий: ")))


class YaDiscUser:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'OAuth {self.token}'}

    def create_folder(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        res = requests.put(url, headers=self.headers, params={'path': folder_name})
        if res.status_code == 201:
            # print(f'\nПапка {folder_name} успешно создана')
            return True
        if res.status_code == 409:
            # print(f'\nПапка {folder_name} уже существует')
            return True  # False

    def get_upLoad_Link(self, file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {'path': file_path, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=self.headers, params=params)
        return response.json()

    def upload_photos(self, path: str, photos: list):
        for photo in tqdm(photos):
            res = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                          params={'path': f"{path}/{photo['file_name']}", 'url': photo['URL_photo']},
                          headers=self.headers)
            if res.status_code == 202:
                pass
        print("Фото успешно загружены на ЯндексДиск")
            #pprint("Ошибка загрузки")


if __name__ == '__main__':
    YaDisc_client = YaDiscUser(
        input("Введите токен пользователя YandexDisc: "))
    x = input('ВВедите название новой папки на ЯндексДиске: ')
    create_folder_status = YaDisc_client.create_folder(x)
    if create_folder_status:
        YaDisc_client.upload_photos(path=x, photos=photos)
