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

def generate_melody(duration=20.0, volume=0.2, sample_rate=44100):
    """Generates a simple looping melody."""
    bpm = 120
    beat_duration = 60 / bpm
    
    # Simple C Major arpeggio / sequence
    notes = [
        261.63, 329.63, 392.00, 523.25, # C, E, G, C
        220.00, 261.63, 329.63, 440.00, # A, C, E, A
        174.61, 220.00, 261.63, 349.23, # F, A, C, F
        196.00, 246.94, 293.66, 392.00  # G, B, D, G
    ]
    
    # Bassline notes (lower octave)
    bass_notes = [130.81, 110.00, 87.31, 98.00] # C, A, F, G
    
    data = bytearray()
    total_samples = int(duration * sample_rate)
    samples_generated = 0
    
    note_index = 0
    bass_index = 0
    
    # 4 beats per bar
    samples_per_beat = int(beat_duration * sample_rate)
    samples_per_note = samples_per_beat // 2 # Eighth notes
    samples_per_bass = samples_per_beat * 4 # Whole note
    
    while samples_generated < total_samples:
        current_note_freq = notes[note_index % len(notes)]
        current_bass_freq = bass_notes[(samples_generated // samples_per_bass) % len(bass_notes)]
        
        # Determine remaining samples for this note
        chunk_size = min(samples_per_note, total_samples - samples_generated)
        
        # Generate mixed wave (Square for lead, Sawtooth for bass)
        # We process sample by sample for mixing, which is slow in Python but fine for this short generation
        # Actually, let's just generate chunks and append
        
        period_lead = sample_rate / current_note_freq
        period_bass = sample_rate / current_bass_freq
        
        for i in range(chunk_size):
            t = samples_generated + i
            
            # Lead (Square)
            val_lead = 1.0 if (t % period_lead) < (period_lead / 2) else -1.0
            
            # Bass (Sawtooth)
            phase_bass = (t % period_bass) / period_bass
            val_bass = 2 * phase_bass - 1
            
            # Mix
            mixed_val = (val_lead * 0.6 + val_bass * 0.4) * 32767 * volume
            
            data += struct.pack('<h', int(mixed_val))
            
        samples_generated += chunk_size
        note_index += 1

    return data

# Generate Sounds
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("Generating sound effects...")
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

    print("Generating soundtrack...")
    # 7. Soundtrack (Looping Melody)
    save_wav("music.wav", generate_melody(duration=16.0, volume=0.15))
    print("Done.")