from PyQt6.QtMultimedia import QMediaPlayer, QSoundEffect, QAudioOutput
from PyQt6.QtCore import QUrl, QObject, QTimer, QSettings
import os
from src.core.logic.abstract_functions import get_resource_path

class SoundManager(QObject):
    _instance = None

    @classmethod
    def get_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("Th1nkItThr0", "Dr1veThr0")
        print("Initializing SoundManager...")
        
        # Store audio outputs to prevent garbage collection
        self.audio_outputs = {}
        
        # Music players
        self.lobby_music = self._create_media_player('audio/music/lobby_music.mp3')
        self.in_game_music = self._create_media_player('audio/music/in_game_music.mp3')
        self.game_end_music = self._create_media_player('audio/music/game_end_music.mp3')
        
        # Sound effects
        self.button_click = self._create_sound_effect('audio/sfx/button_click.wav')
        self.error_notify = self._create_sound_effect('audio/sfx/error_notify.wav')
        self.success_notify = self._create_sound_effect('audio/sfx/success_notify.wav')
        self.car_arrival = self._create_sound_effect('audio/sfx/car_arrival.wav')
        self.customer_order = self._create_sound_effect('audio/sfx/customer_order.wav')
        self.daily_deals_update = self._create_sound_effect('audio/sfx/daily_deals_update.wav')
        self.time_ticking = self._create_sound_effect('audio/sfx/time_ticking.wav')
        self.bad_code = self._create_sound_effect('audio/sfx/bad_code.wav')
        self.out_of_time = self._create_sound_effect('audio/sfx/out_of_time.wav')
        self.correct_code = self._create_sound_effect('audio/sfx/correct_code.wav')
        self.new_highscore = self._create_sound_effect('audio/sfx/new_highscore.wav')
        self.game_start = self._create_sound_effect('audio/sfx/game_start.wav')
        
        self._update_volumes()
        self._preload_sounds()

    @property
    def music_enabled(self):
        return self.settings.value("music_enabled", True, type=bool)

    @music_enabled.setter
    def music_enabled(self, value):
        self.settings.setValue("music_enabled", value)
        if not value:
            self.stop_all()

    @property
    def sfx_enabled(self):
        return self.settings.value("sfx_enabled", True, type=bool)

    @sfx_enabled.setter
    def sfx_enabled(self, value):
        self.settings.setValue("sfx_enabled", value)

    @property
    def music_volume(self):
        return self.settings.value("music_volume", 0.5, type=float)

    @music_volume.setter
    def music_volume(self, value):
        self.settings.setValue("music_volume", value)
        for player in [self.lobby_music, self.in_game_music, self.game_end_music]:
            audio_output = player.audioOutput()
            if audio_output:
                audio_output.setVolume(value)

    @property
    def sfx_volume(self):
        return self.settings.value("sfx_volume", 0.8, type=float)

    @sfx_volume.setter
    def sfx_volume(self, value):
        self.settings.setValue("sfx_volume", value)
        for effect in [self.button_click, self.error_notify, self.success_notify, 
                       self.car_arrival, self.customer_order, self.daily_deals_update, 
                       self.time_ticking, self.bad_code, self.out_of_time, 
                       self.correct_code, self.new_highscore, self.game_start]:
            effect.setVolume(value)

    def _create_media_player(self, relative_path):
        player = QMediaPlayer()
        audio_output = QAudioOutput()
        audio_output.setVolume(self.music_volume)
        player.setAudioOutput(audio_output)
        self.audio_outputs[player] = audio_output
        file_path = get_resource_path(relative_path)
        if not os.path.exists(file_path):
            print(f"Error: Audio file not found: {file_path}")
            return player
        player.setSource(QUrl.fromLocalFile(file_path))
        player.errorOccurred.connect(lambda err: print(f"QMediaPlayer error for {relative_path}: {err}, {player.errorString()}"))
        QTimer.singleShot(100, lambda: self._preload_media_player(player, relative_path))
        return player

    def _preload_media_player(self, player, relative_path):
        if player.audioOutput() is None:
            audio_output = QAudioOutput()
            audio_output.setVolume(self.music_volume)
            player.setAudioOutput(audio_output)
            self.audio_outputs[player] = audio_output
        player.play()
        QTimer.singleShot(100, player.stop)
        status = player.mediaStatus()
        print(f"Preloaded {relative_path}: Status = {self._media_status_to_string(status)}")
        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            print(f"Retrying preload for {relative_path}...")
            player.setSource(QUrl())
            player.setSource(QUrl.fromLocalFile(get_resource_path(relative_path)))
            player.play()
            QTimer.singleShot(100, player.stop)
            print(f"Retry status: {self._media_status_to_string(player.mediaStatus())}")

    def _create_sound_effect(self, relative_path):
        effect = QSoundEffect()
        file_path = get_resource_path(relative_path)
        if not os.path.exists(file_path):
            print(f"Error: Audio file not found: {file_path}")
            return effect
        effect.setSource(QUrl.fromLocalFile(file_path))
        effect.setVolume(self.sfx_volume)
        effect.setLoopCount(1)
        effect.play()
        effect.stop()
        return effect

    def _media_status_to_string(self, status):
        statuses = {
            QMediaPlayer.MediaStatus.NoMedia: "NoMedia",
            QMediaPlayer.MediaStatus.LoadingMedia: "LoadingMedia",
            QMediaPlayer.MediaStatus.LoadedMedia: "LoadedMedia",
            QMediaPlayer.MediaStatus.StalledMedia: "StalledMedia",
            QMediaPlayer.MediaStatus.BufferingMedia: "BufferingMedia",
            QMediaPlayer.MediaStatus.BufferedMedia: "BufferedMedia",
            QMediaPlayer.MediaStatus.EndOfMedia: "EndOfMedia",
            QMediaPlayer.MediaStatus.InvalidMedia: "InvalidMedia",
        }
        return statuses.get(status, "Unknown")

    def _playback_state_to_string(self, state):
        states = {
            QMediaPlayer.PlaybackState.StoppedState: "StoppedState",
            QMediaPlayer.PlaybackState.PlayingState: "PlayingState",
            QMediaPlayer.PlaybackState.PausedState: "PausedState"
        }
        return states.get(state, "Unknown")

    def _preload_sounds(self):
        for effect in [self.button_click, self.error_notify, self.success_notify, 
                       self.car_arrival, self.customer_order, self.daily_deals_update, 
                       self.time_ticking, self.bad_code, self.out_of_time, 
                       self.correct_code, self.new_highscore, self.game_start]:
            if effect.source().isValid():
                effect.play()
                effect.stop()
        for player in [self.lobby_music, self.in_game_music, self.game_end_music]:
            if player.source().isValid():
                player.setLoops(1)
                player.play()
                QTimer.singleShot(100, player.stop)

    def _update_volumes(self):
        for player in [self.lobby_music, self.in_game_music, self.game_end_music]:
            audio_output = player.audioOutput()
            if audio_output is None:
                audio_output = QAudioOutput()
                audio_output.setVolume(self.music_volume)
                player.setAudioOutput(audio_output)
                self.audio_outputs[player] = audio_output
            audio_output.setVolume(self.music_volume)
        for effect in [self.button_click, self.error_notify, self.success_notify, 
                       self.car_arrival, self.customer_order, self.daily_deals_update, 
                       self.time_ticking, self.bad_code, self.out_of_time, 
                       self.correct_code, self.new_highscore, self.game_start]:
            effect.setVolume(self.sfx_volume)

    def play_effect(self, effect):
        if self.sfx_enabled and not effect.isPlaying():
            self.stop_all_effects()
            effect.play()

    def play_music(self, player, retry_count=0):
        if not self.music_enabled:
            return
        if player.audioOutput() is None:
            audio_output = QAudioOutput()
            audio_output.setVolume(self.music_volume)
            player.setAudioOutput(audio_output)
            self.audio_outputs[player] = audio_output
        status = player.mediaStatus()
        if status in [QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia]:
            player.setLoops(-1)
            player.play()
            print(f"Playing music, status: {self._media_status_to_string(status)}")
        else:
            print(f"Cannot play music, invalid status: {self._media_status_to_string(status)}")
            if retry_count < 2:
                print(f"Retrying music playback (attempt {retry_count + 1})...")
                player.setSource(QUrl())
                player.setSource(QUrl.fromLocalFile(player.source().toLocalFile()))
                QTimer.singleShot(500, lambda: self.play_music(player, retry_count + 1))

    def stop_all_effects(self):
        for effect in [self.button_click, self.error_notify, self.success_notify, 
                       self.car_arrival, self.customer_order, self.daily_deals_update, 
                       self.time_ticking, self.bad_code, self.out_of_time, 
                       self.correct_code, self.new_highscore, self.game_start]:
            effect.stop()

    def stop_all(self):
        for player in [self.lobby_music, self.in_game_music, self.game_end_music]:
            player.stop()
        self.stop_all_effects()