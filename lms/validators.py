import re
from rest_framework.serializers import ValidationError
from urllib.parse import urlparse

class LinkYouTubeValidator:

    def __init__(self, link_field):
        self.link_field = link_field

    def __call__(self, value):

        # Получаем значение поля с ссылкой
        url = value.get(self.link_field)

        if not url:
            return # Если ссылки нет, ничего не проверяем

        # Парсим URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Проверяем, является ли домен YouTube
        if domain not in ['youtube.com', 'www.youtube.com']:
            raise ValidationError(
                f"Запрещена ссылка на {url}. Разрешены только ссылки на youtube.com"
            )

        # Дополнительно проверяем формат URL через регулярное выражение
        youtube_pattern = re.compile(r'https?://(www\.)?youtube\.com/.*')

        if not youtube_pattern.match(url):
            raise ValidationError(
                f"Некорректный формат ссылки {url}. Проверьте правильность URL"
            )
