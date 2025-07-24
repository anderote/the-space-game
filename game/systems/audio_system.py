import pygame
import os
import random
from typing import Dict, Optional

class AudioSystem:
    """Manages all audio effects and background music for the game."""
    
    def __init__(self):
        """Initialize the audio system."""
        # Initialize pygame mixer with optimized settings
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Audio settings
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        self.enabled = True
        
        # Sound caches
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_variations: Dict[str, list] = {}
        
        # Channel management
        self.laser_channel = pygame.mixer.Channel(0)
        self.explosion_channel = pygame.mixer.Channel(1)
        self.ui_channel = pygame.mixer.Channel(2)
        self.ambient_channel = pygame.mixer.Channel(3)
        
        # Generate procedural sounds
        self._generate_sounds()
        
        print("🔊 Audio system initialized!")
    
    def _generate_sounds(self):
        """Generate procedural sound effects."""
        try:
            # Laser sounds (different pitches)
            laser_sounds = []
            for i in range(3):
                laser_sound = self._generate_laser_sound(440 + i * 220)  # Different frequencies
                laser_sounds.append(laser_sound)
            self.sound_variations['laser'] = laser_sounds
            
            # Explosion sounds (different intensities)
            explosion_sounds = []
            for i in range(2):
                explosion_sound = self._generate_explosion_sound(intensity=0.6 + i * 0.3)
                explosion_sounds.append(explosion_sound)
            self.sound_variations['explosion'] = explosion_sounds
            
            # UI sounds
            self.sounds['place_building'] = self._generate_place_sound()
            self.sounds['button_click'] = self._generate_click_sound()
            self.sounds['error'] = self._generate_error_sound()
            self.sounds['upgrade'] = self._generate_upgrade_sound()
            
            # Combat sounds
            self.sounds['missile_launch'] = self._generate_missile_sound()
            self.sounds['shield_hit'] = self._generate_shield_sound()
            
            print(f"✅ Generated {len(self.sounds) + sum(len(v) for v in self.sound_variations.values())} procedural sounds")
            
        except Exception as e:
            print(f"⚠️ Could not generate sounds: {e}")
            self.enabled = False
    
    def _generate_laser_sound(self, frequency: float) -> pygame.mixer.Sound:
        """Generate a laser sound with the given frequency."""
        import numpy as np
        
        duration = 0.2  # 200ms
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate laser sound wave
        t = np.linspace(0, duration, frames)
        
        # Main frequency component with harmonic
        wave = np.sin(frequency * 2 * np.pi * t) * 0.3
        wave += np.sin(frequency * 3 * 2 * np.pi * t) * 0.1  # Harmonic
        
        # Add rapid frequency sweep for "pew" effect
        sweep = np.sin((frequency + 200 * np.exp(-t * 10)) * 2 * np.pi * t) * 0.4
        wave += sweep
        
        # Envelope for attack and decay
        envelope = np.exp(-t * 8)  # Exponential decay
        wave *= envelope
        
        # Convert to pygame sound
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        sound = pygame.sndarray.make_sound(stereo_wave)
        
        return sound
    
    def _generate_explosion_sound(self, intensity: float) -> pygame.mixer.Sound:
        """Generate an explosion sound with the given intensity."""
        import numpy as np
        
        duration = 0.8  # 800ms
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate explosion using filtered noise
        t = np.linspace(0, duration, frames)
        
        # White noise base
        noise = np.random.uniform(-1, 1, frames) * intensity
        
        # Low frequency rumble
        rumble_freq = 60 + intensity * 40
        rumble = np.sin(rumble_freq * 2 * np.pi * t) * 0.4
        
        # Sharp attack component
        attack = np.sin(800 * 2 * np.pi * t) * np.exp(-t * 15) * 0.6
        
        # Combine components
        wave = noise * 0.5 + rumble + attack
        
        # Envelope
        envelope = np.exp(-t * 2)  # Slower decay for explosion
        wave *= envelope
        
        # Limit amplitude
        wave = np.clip(wave, -1, 1)
        
        # Convert to pygame sound
        wave = (wave * 32767 * 0.8).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        sound = pygame.sndarray.make_sound(stereo_wave)
        
        return sound
    
    def _generate_place_sound(self) -> pygame.mixer.Sound:
        """Generate a building placement sound."""
        import numpy as np
        
        duration = 0.3
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames)
        
        # Rising frequency sweep
        freq_start = 200
        freq_end = 600
        freq_sweep = freq_start + (freq_end - freq_start) * (t / duration)
        
        wave = np.sin(freq_sweep * 2 * np.pi * t)
        
        # Add harmonic
        wave += np.sin(freq_sweep * 1.5 * 2 * np.pi * t) * 0.3
        
        # Envelope
        envelope = np.exp(-t * 3)
        wave *= envelope * 0.5
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_click_sound(self) -> pygame.mixer.Sound:
        """Generate a UI click sound."""
        import numpy as np
        
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames)
        
        # Short click
        wave = np.sin(800 * 2 * np.pi * t) * np.exp(-t * 20)
        wave += np.sin(1200 * 2 * np.pi * t) * np.exp(-t * 25) * 0.5
        
        wave = (wave * 32767 * 0.3).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_error_sound(self) -> pygame.mixer.Sound:
        """Generate an error/invalid action sound."""
        import numpy as np
        
        duration = 0.4
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames)
        
        # Descending tone
        freq_start = 400
        freq_end = 200
        freq_sweep = freq_start + (freq_end - freq_start) * (t / duration)
        
        wave = np.sin(freq_sweep * 2 * np.pi * t)
        
        # Envelope
        envelope = np.exp(-t * 4)
        wave *= envelope * 0.4
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_upgrade_sound(self) -> pygame.mixer.Sound:
        """Generate an upgrade success sound."""
        import numpy as np
        
        duration = 0.5
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames)
        
        # Ascending arpeggio
        freqs = [261.63, 329.63, 392.00, 523.25]  # C, E, G, C octave
        wave = np.zeros(frames)
        
        for i, freq in enumerate(freqs):
            start_frame = int(i * frames / len(freqs))
            end_frame = int((i + 1) * frames / len(freqs))
            if end_frame > frames:
                end_frame = frames
                
            segment_t = t[start_frame:end_frame] - t[start_frame]
            segment_wave = np.sin(freq * 2 * np.pi * segment_t) * np.exp(-segment_t * 3)
            wave[start_frame:end_frame] = segment_wave
        
        wave *= 0.4
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_missile_sound(self) -> pygame.mixer.Sound:
        """Generate a missile launch sound."""
        import numpy as np
        
        duration = 0.6
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames)
        
        # Whoosh effect
        noise = np.random.uniform(-1, 1, frames) * 0.3
        
        # Low frequency component
        low_freq = 80
        low_wave = np.sin(low_freq * 2 * np.pi * t) * 0.5
        
        # High frequency sweep
        high_freq = 1000 * np.exp(-t * 2)
        high_wave = np.sin(high_freq * 2 * np.pi * t) * 0.3
        
        wave = noise + low_wave + high_wave
        
        # Envelope
        envelope = np.exp(-t * 1.5)
        wave *= envelope * 0.6
        
        wave = np.clip(wave, -1, 1)
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        return pygame.sndarray.make_sound(stereo_wave)
    
    def _generate_shield_sound(self) -> pygame.mixer.Sound:
        """Generate a shield hit sound."""
        import numpy as np
        
        duration = 0.3
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames)
        
        # Metallic ring
        freq = 1200
        wave = np.sin(freq * 2 * np.pi * t)
        wave += np.sin(freq * 1.5 * 2 * np.pi * t) * 0.3
        wave += np.sin(freq * 2.1 * 2 * np.pi * t) * 0.2
        
        # Rapid decay
        envelope = np.exp(-t * 10)
        wave *= envelope * 0.4
        
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.array([wave, wave]).T
        return pygame.sndarray.make_sound(stereo_wave)
    
    def play_sound(self, sound_name: str, volume: float = 1.0, channel: Optional[pygame.mixer.Channel] = None):
        """Play a sound effect."""
        if not self.enabled:
            return
            
        try:
            # Handle sound variations
            if sound_name in self.sound_variations:
                sound = random.choice(self.sound_variations[sound_name])
            elif sound_name in self.sounds:
                sound = self.sounds[sound_name]
            else:
                return
            
            # Calculate final volume
            final_volume = volume * self.sfx_volume * self.master_volume
            sound.set_volume(final_volume)
            
            # Play on specific channel if provided
            if channel:
                channel.play(sound)
            else:
                pygame.mixer.play(sound)
                
        except Exception as e:
            print(f"⚠️ Error playing sound {sound_name}: {e}")
    
    def play_laser(self, volume: float = 1.0):
        """Play a laser sound effect."""
        self.play_sound('laser', volume, self.laser_channel)
    
    def play_explosion(self, volume: float = 1.0):
        """Play an explosion sound effect."""
        self.play_sound('explosion', volume, self.explosion_channel)
    
    def play_ui_sound(self, sound_name: str, volume: float = 1.0):
        """Play a UI sound effect."""
        self.play_sound(sound_name, volume, self.ui_channel)
    
    def set_master_volume(self, volume: float):
        """Set the master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_sfx_volume(self, volume: float):
        """Set the sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def toggle_enabled(self):
        """Toggle audio on/off."""
        self.enabled = not self.enabled
        
    def shutdown(self):
        """Clean up audio resources."""
        pygame.mixer.quit()
        print("🔇 Audio system shut down") 