import os

import telebot
from dotenv import load_dotenv

import logger

log = logger.get_logger(__name__)
from torrent.client import TorrentClient
from torrent.downloader import TorrentDownloader

torrent_downloader = TorrentDownloader()
torrent_client = TorrentClient()

load_dotenv()

class MyBot:
    def __init__(self):
        self.bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
        self.message = None
        self.call = None
        """Обработчик комманды start"""
        @self.bot.message_handler(commands=["start"])
        def __start_handler(message):
            self.message=message
            self.menu()

        @self.bot.message_handler(commands=["remove_torrent"])
        def __remove_torrent_handler(message):
            torrent_client.remove_torrent()
            os.remove('./torrents/torrent_file.torrent')
            self.bot.send_message(message.chat.id, "Торрент успешно удален.")

        """Обработчик команды остановки скачивания торрента"""
        @self.bot.message_handler(commands=["stop"])
        def __stop_download_handler(message):
            torrent_client.stop_download()
            self.bot.send_message(message.chat.id, "Загрузка остановлена и файлы удалены.")
            self.delete_downloads()
            # удаляем торрент-файл
            os.remove('./torrents/torrent_file.torrent')
            self.bot.send_message(message.chat.id, "Скачивание остановлено и торрент-файл удален.")


        @self.bot.message_handler(commands=["status"])
        def __status_handler(message):
            statuses = torrent_client.get_torrents_status()
            if not statuses:
                self.bot.send_message(message.chat.id, "Нет активных загрузок")
                return
            response = "Статус загрузок:\n"
            for status in statuses:
                response += f"Название: {status['name']}\nПрогресс: {status['progress']:.2f}%\n\n"
            self.bot.send_message(message.chat.id, response)


        @self.bot.message_handler(content_types=['document'])
        def __download_torrent_handler(message):
            # Получаем информацию о файле
            file_info = self.bot.get_file(message.document.file_id)
            # Скачиваем файл на сервер бота
            downloaded_file = self.bot.download_file(file_info.file_path)
            # Сохраняем файл на диск
            with open('./torrents/torrent_file.torrent', 'wb') as f:
                f.write(downloaded_file)
            self.bot.reply_to(message, f'Торрент файл сохранен')
            torrent_client.start_session()
            torrent_client.add_torrent_file('/home/tozix/dev/torrent-bot/torrents/torrent_file.torrent')
            # Запускаем загрузку торрента в фоновом режиме
            torrent_client.start_download()
            # Отправляем пользователю сообщение, что загрузка началась
            self.bot.send_message(message.chat.id, "Загрузка началась!")

        """Обработчик callback"""
        @self.bot.callback_query_handler(func=lambda call: True)
        def __callback_worker(call):
            self.call=call
            self.callback_handler()
        
        """Обработчик сообщений"""
        @self.bot.message_handler(func=lambda message: True)
        def __message_worker(message):
            self.message=message
            self.message_handler()

    def start(self):
        log.debug("Успешный запуск бота")
        self.bot.polling(none_stop=True)

    def menu(self):
        self.menu_keyboard = telebot.types.InlineKeyboardMarkup()
        self.menu_keyboard.add(telebot.types.InlineKeyboardButton(text="Остановить загрузки", callback_data="stop_torrent"))
        self.menu_keyboard.add(telebot.types.InlineKeyboardButton(text="Скачать файл по ссылке", callback_data="download_link"))
        self.menu_keyboard.add(telebot.types.InlineKeyboardButton(text="Мои загрузки", callback_data="my_downloads"))
        self.menu_keyboard.add(telebot.types.InlineKeyboardButton(text="Настройки", callback_data="settings"))

        self.bot.send_message(self.message.chat.id, "Привет! Что вы хотите сделать?", reply_markup=self.menu_keyboard)

    
    def message_handler(self):
        self.bot.send_message(self.message.chat.id, "Ты прислал мне сообщение!.")

    def callback_handler(self):
        if self.call.data == "stop_torrent":
            self.bot.send_message(self.call.message.chat.id, "Остановить загрузки")
            self.stop_download()
        if self.call.data == "download_file":
            self.bot.send_message(self.call.message.chat.id, "Скачать файл по ссылке")
        if self.call.data == "my_downloads":
            self.get_status()
            self.bot.send_message(self.call.message.chat.id, "Мои загрузки")
        if self.call.data == "settings":
            self.bot.send_message(self.call.message.chat.id, "Настройки")
    

    def get_status(self):
        statuses = torrent_client.get_torrents_status()
        if not statuses:
            self.bot.send_message(self.message.chat.id, "Нет активных загрузок")
            return
        response = "Статус загрузок:\n"
        for status in statuses:
            response += f"Название: {status['name']}\nПрогресс: {status['progress']:.2f}%\n\n"
        self.bot.send_message(self.message.chat.id, response)       

    def delete_downloads(self):
        download_dir = './downloads'
        for root, dirs, files in os.walk(download_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    os.remove(file_path)
                    log.info(f'Файл {file_path} успешно удален')
                except FileNotFoundError:
                    log.warning(f'Файл {file_path} не найден')
                except OSError as e:
                    log.error(f'Ошибка удаления файла {file_path}: {e}')

    def stop_download(self):
        try:
            torrent_client.stop_download()
            self.bot.send_message(self.message.chat.id, "Загрузка остановлена и файлы удалены.")
            self.delete_downloads()
            # удаляем торрент-файл
            os.remove('./torrents/torrent_file.torrent')
            self.bot.send_message(self.message.chat.id, "Скачивание остановлено и торрент-файл удален.")
        except Exception as e:
            self.bot.send_message(self.message.chat.id, f"Произошла ошибка при остановке загрузки: {e}")
