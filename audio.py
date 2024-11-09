from pydub import AudioSegment
import scipy.signal
import numpy as np

def apply_slowed_reverb(audio_path, output_path, slow_factor=0.96, reverb_decay=0.5, reverb_delay_ms=200, output_format="mp3"):
    # Load audio file
    sound = AudioSegment.from_file(audio_path)
    
    # Step 1: Slow down the audio
    slowed_sound = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * slow_factor)
    }).set_frame_rate(sound.frame_rate)  # Retain original frame rate to keep output compatible

    # Step 2: Convert slowed audio to numpy array for processing
    samples = np.array(slowed_sound.get_array_of_samples())

    # Step 3: Create reverb kernel (Decay + Delay)
    delay_samples = int(reverb_delay_ms * slowed_sound.frame_rate / 1000)
    reverb_kernel = np.zeros(delay_samples + 1)
    reverb_kernel[0] = 1
    reverb_kernel[delay_samples] = reverb_decay

    # Apply reverb effect using convolution with the reverb kernel
    reverb_samples = scipy.signal.fftconvolve(samples, reverb_kernel, mode='full')

    # Normalize and convert back to original dtype
    reverb_samples = np.int16(reverb_samples / np.max(np.abs(reverb_samples)) * 32767)

    # Step 4: Create an AudioSegment from reverb samples and export as mp3
    reverb_sound = slowed_sound._spawn(reverb_samples.astype(np.int16).tobytes())
    reverb_sound.export(output_path, format=output_format)

# Usage example
apply_slowed_reverb("wow.mp3", "output_slowed_reverb.mp3", slow_factor=0.9, reverb_decay=0.4, reverb_delay_ms=250, output_format="mp3")
