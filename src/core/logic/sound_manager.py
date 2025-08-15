from PyQt6.QtMultimedia import QMediaPlayer, QSoundEffect, QAudioOutput
from PyQt6.QtCore import QUrl, QObject, QTimer
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
        print("Initializing SoundManager...")
        
        # Define volumes first
        self.music_volume = 0.5
        self.sfx_volume = 0.8
        
        # Store audio outputs separately to ensure they persist
        self.audio_outputs = {}
        
        # Music players
        self.lobby_music = self._create_media_player('audio/music/lobby_music.mp3', 'lobby')
        self.in_game_music = self._create_media_player('audio/music/in_game_music.mp3', 'in_game')
        self.game_end_music = self._create_media_player('audio/music/game_end_music.mp3', 'game_end')
        
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
        
        # Update volumes after creating players with a small delay to ensure initialization
        QTimer.singleShot(200, self._update_volumes)
        
        # Preload all sounds with a delay
        QTimer.singleShot(300, self._preload_sounds)

    def _create_media_player(self, relative_path, key):
        player = QMediaPlayer(self)  # Set parent to ensure proper cleanup
        
        # Create audio output and store it
        audio_output = QAudioOutput(self)  # Set parent to ensure proper cleanup
        audio_output.setVolume(self.music_volume)
        self.audio_outputs[key] = audio_output  # Store reference to prevent garbage collection
        
        # Set the audio output
        player.setAudioOutput(audio_output)
        
        file_path = get_resource_path(relative_path)
        if not os.path.exists(file_path):
            print(f"Error: Audio file not found: {file_path}")
            return player
        
        player.setSource(QUrl.fromLocalFile(file_path))
        player.errorOccurred.connect(lambda err: print(f"QMediaPlayer error for {relative_path}: {err}, {player.errorString()}"))
        player.playbackStateChanged.connect(lambda state: print(f"Playback state for {relative_path}: {self._playback_state_to_string(state)}"))
        
        # Delay the preload to ensure the player is fully initialized
        QTimer.singleShot(150, lambda: self._preload_media_player(player, relative_path))
        
        return player

    def _preload_media_player(self, player, relative_path):
        # Ensure the audio output is still valid
        if player.audioOutput() is None:
            print(f"Warning: Audio output lost for {relative_path}, recreating...")
            # Find the corresponding audio output and reassign
            for key, audio_output in self.audio_outputs.items():
                if key in relative_path:
                    player.setAudioOutput(audio_output)
                    break
        
        player.play()
        player.stop()
        status = player.mediaStatus()
        print(f"Preloaded {relative_path}: Status = {self._media_status_to_string(status)}")
        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            print(f"Retrying preload for {relative_path}...")
            player.setSource(QUrl())
            player.setSource(QUrl.fromLocalFile(get_resource_path(relative_path)))
            player.play()
            player.stop()
            print(f"Retry status: {self._media_status_to_string(player.mediaStatus())}")

    def _create_sound_effect(self, relative_path):
        effect = QSoundEffect(self)  # Set parent
        file_path = get_resource_path(relative_path)
        if not os.path.exists(file_path):
            print(f"Error: Audio file not found: {file_path}")
            return effect
        effect.setSource(QUrl.fromLocalFile(file_path))
        effect.setVolume(self.sfx_volume)
        # Test the sound effect
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
        effects = [self.button_click, self.error_notify, self.success_notify, 
                  self.car_arrival, self.customer_order, self.daily_deals_update, 
                  self.time_ticking, self.bad_code, self.out_of_time, 
                  self.correct_code, self.new_highscore, self.game_start]
        
        for effect in effects:
            if effect and effect.source().isValid():
                effect.play()
                effect.stop()
            else:
                print(f"Warning: Invalid sound effect: {effect}")

        players = [self.lobby_music, self.in_game_music, self.game_end_music]
        for player in players:
            if player and player.source().isValid():
                # Ensure audio output is still connected
                if player.audioOutput() is None:
                    print(f"Warning: Reconnecting audio output for player")
                    # Reconnect audio output
                    for key, audio_output in self.audio_outputs.items():
                        player.setAudioOutput(audio_output)
                        break
                player.setLoops(1)
                player.play()
                player.stop()

    def _update_volumes(self):
        print("Updating volumes...")
        players = [self.lobby_music, self.in_game_music, self.game_end_music]
        
        for i, player in enumerate(players):
            if player:
                audio_output = player.audioOutput()
                if audio_output is not None:
                    audio_output.setVolume(self.music_volume)
                    print(f"Set music volume to {self.music_volume} for player {i}")
                else:
                    print(f"Warning: No audio output for player {i} - checking stored outputs")
                    # Try to reassign from stored outputs
                    if i < len(self.audio_outputs):
                        keys = list(self.audio_outputs.keys())
                        if i < len(keys):
                            audio_output = self.audio_outputs[keys[i]]
                            player.setAudioOutput(audio_output)
                            audio_output.setVolume(self.music_volume)
                            print(f"Reassigned and set volume for player {i}")

        effects = [self.button_click, self.error_notify, self.success_notify, 
                  self.car_arrival, self.customer_order, self.daily_deals_update, 
                  self.time_ticking, self.bad_code, self.out_of_time, 
                  self.correct_code, self.new_highscore, self.game_start]
        
        for effect in effects:
            if effect:
                effect.setVolume(self.sfx_volume)

    def play_effect(self, effect):
        if not effect:
            print("Warning: Trying to play None effect")
            return
        if effect.isPlaying():
            return
        self.stop_all_effects()
        effect.play()

    def play_music(self, player, retry_count=0):
        if not player:
            print("Warning: Trying to play None player")
            return
            
        # Ensure audio output is connected
        if player.audioOutput() is None:
            print("Warning: No audio output, trying to reconnect...")
            for key, audio_output in self.audio_outputs.items():
                player.setAudioOutput(audio_output)
                break
        
        if player.mediaStatus() in [QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia]:
            player.setLoops(-1)
            player.play()
            print(f"Playing music, status: {self._media_status_to_string(player.mediaStatus())}")
        else:
            print(f"Cannot play music, invalid status: {self._media_status_to_string(player.mediaStatus())}")
            if retry_count < 2:
                print(f"Retrying music playback (attempt {retry_count + 1})...")
                QTimer.singleShot(500, lambda: self.play_music(player, retry_count + 1))

    def stop_all_effects(self):
        effects = [self.button_click, self.error_notify, self.success_notify, 
                  self.car_arrival, self.customer_order, self.daily_deals_update, 
                  self.time_ticking, self.bad_code, self.out_of_time, 
                  self.correct_code, self.new_highscore, self.game_start]
        
        for effect in effects:
            if effect:
                effect.stop()

    def stop_all(self):
        players = [self.lobby_music, self.in_game_music, self.game_end_music]
        for player in players:
            if player:
                player.stop()
        self.stop_all_effects()