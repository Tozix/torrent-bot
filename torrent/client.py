import threading
import time

import logger

log = logger.get_logger(__name__)

import libtorrent as lt


class TorrentClient:
    def __init__(self):
        self.session = None
        self.torrents = {}
        self.download_thread = None
        self.stop_event = threading.Event()

    def start_session(self):
        self.session = lt.session()
        self.session.listen_on(6881, 6891)


    def add_torrent_file(self, torrent_file):
        info = lt.torrent_info(torrent_file)
        handle = self.session.add_torrent({
            'ti': info,
            'save_path': './downloads',
            'storage_mode': lt.storage_mode_t(2),
        })
        handle.pause()  # добавить торрент с флагом paused=True
        self.torrents[handle] = {
            'status': handle.status().state,
            'progress': handle.status().progress,
            'name': info.name(),
            'size': info.total_size()
        }

    def start_download(self):
        if not self.download_thread or not self.download_thread.is_alive():
            self.download_thread = threading.Thread(target=self._download_thread_func)
            self.download_thread.start()

    def _download_thread_func(self):
        while not self.stop_event.is_set():
            for handle, status in self.torrents.items():
                if status['status'] == lt.torrent_status.paused:
                    handle.resume()
                elif status['status'] == lt.torrent_status.downloading:
                    log.info(f"Downloading {status['name']}: {status['progress'] * 100:.2f}%")
            time.sleep(1)

    def stop_download(self):
        self.stop_event.set()

    def get_torrents_status(self):
        torrents_status = []
        for handle, status in self.torrents.items():
            status = handle.status()
            torrents_status.append({
                'status': status.state,
                'progress': status.progress,
                'name': status.name,
                'size': status.total_wanted,
                'downloaded': status.total_wanted_done
            })
        return torrents_status

    def remove_torrent(self, handle):
        if handle in self.torrents:
            handle.pause()
            self.session.remove_torrent(handle)
            del self.torrents[handle]