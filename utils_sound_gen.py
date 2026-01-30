import wave
import math
import struct
import random
import os

OUTPUT_DIR = "assets/sounds"

def save_wav(filename, data, sample_rate=44100):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with wave.open(filepath, 'w') as f:
        f.setnchannels(1)  # Mono
        f.setsampwidth(2)  # 2 bytes per sample (16-bit PCM)
        f.setframerate(sample_rate)
        f.writeframes(data)
    print(f"Generated {filepath}")

def generate_square_wave(frequency, duration, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    data = bytearray()
    period = sample_rate / frequency
    for i in range(n_samples):
        value = 32767 * volume if (i % period) < (period / 2) else -32768 * volume
        data += struct.pack('<h', int(value))
    return data

def generate_noise(duration, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    data = bytearray()
    for i in range(n_samples):
        value = random.randint(-32768, 32767) * volume
        data += struct.pack('<h', int(value))
    return data

def generate_sawtooth(start_freq, end_freq, duration, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    data = bytearray()
    for i in range(n_samples):
        progress = i / n_samples
        freq = start_freq + (end_freq - start_freq) * progress
        period = sample_rate / freq
        phase = (i % period) / period
        value = (2 * phase - 1) * 32767 * volume
        data += struct.pack('<h', int(value))
    return data

# Generate Sounds
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Menu Select (Short high blip)
    save_wav("select.wav", generate_square_wave(880, 0.05, 0.3))

    # 2. Shoot (Slide down pitch)
    save_wav("shoot.wav", generate_sawtooth(880, 110, 0.15, 0.3))

    # 3. Jump (Slide up pitch)
    save_wav("jump.wav", generate_sawtooth(220, 660, 0.1, 0.3))

    # 4. Explosion (Noise)
    save_wav("explosion.wav", generate_noise(0.3, 0.4))
    
    # 5. Game Over (Descending low tones)
    save_wav("gameover.wav", generate_sawtooth(200, 50, 0.5, 0.4))

    # 6. Score (Ding)
    save_wav("score.wav", generate_square_wave(1200, 0.1, 0.3))
