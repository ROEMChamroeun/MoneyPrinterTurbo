# ប_សន_គ_ស_ម_ត_ស_ទ_ធ_Bours_Neak_Samouth_Sothea — studio (TikTok / Reels / Shorts)

**FAIL**

| Check | Before | After | Target |
|---|---|---|---|
| Loudness | -12.1 LUFS | -14.0 LUFS | -14 ±0.5 |
| True peak | 0.2 dBTP | -2.0 dBTP | ≤ -1.5 |
| Loudness range | 3.4 LU | 3.4 LU | ≤ 6 |
| Noise floor | -17 dBFS | -19 dBFS | ≤ -60 dBFS |
| Sibilance | -24.3 dB | -27.5 dB | ≤ -6 |
| Low bursts | -3.8 dB | -3.5 dB | ≤ -10 |
| Phrase spread | ±0.4 dB | ±0.2 dB | ≤ ±2 |
| Tilt | -4.6 dB/oct | -4.8 dB/oct | info |
| Bandwidth | 24.0 kHz | 24.0 kHz | info |
| Limiter depth | - | 0.3 dB | ≤ 4 |

## Checks

- ✓ loudness -14.0 LUFS vs target -14
- ✓ true peak -2.0 dBTP (max -1.5)
- ✓ loudness range 3.4 LU
- ✗ noise floor -19 dBFS (SNR 7 dB): audible hiss/hum, denoise
- ✓ sibilance -27.5 dB
- ! low-end bursts -3.5 dB: plosives or rumble, steeper high-pass

## Chain

0. ffmpeg: declip, denoise nr 20 dB, floor -20 dB
1. **eq_7band** {"hpf_on": 1, "hpf_freq": 60, "hpf_slope": 2} — high-pass 60 Hz (18 dB/oct) under the voice (lowest pitch ~75 Hz): removes rumble and thumps without thinning it
2. **compressor** {"threshold": -3.0, "ratio": 4, "attack": 1, "release": 60, "knee": 3, "lookahead": 2} — fast peak control so the limiter works lightly (peak-to-loudness goal ≤ 14.5 dB)
3. **eq_7band** {"low_mid_freq": 300, "low_mid_gain": -1.5, "low_mid_q": 1.0, "high_mid_freq": 4500, "high_mid_gain": 1.5, "high_mid_q": 0.9, "high_shelf_freq": 11000, "high_shelf_gain": 1.5, "high_shelf_q": 0.707} — polish: clear a little boxiness at 300 Hz, add presence at 4.5 kHz and air above 11 kHz
- master: gain -1.17 dB -> maximizer ceiling -2.0 dB (1 loudness passes)

## Notes

- compressor threshold tuned to -3.0: plr 12.4 (goal 13.0..14.5, out of reach)

## Files

- /home/ubuntu/CHR/sound-engineer/jobs/ប_សន_គ_ស_ម_ត_ស_ទ_ធ_Bours_Neak_Samouth_Sothea/studio/out/ប_សន_គ_ស_ម_ត_ស_ទ_ធ_Bours_Neak_Samouth_Sothea_studio.wav
- /home/ubuntu/CHR/sound-engineer/jobs/ប_សន_គ_ស_ម_ត_ស_ទ_ធ_Bours_Neak_Samouth_Sothea/studio/out/AB_ប_សន_គ_ស_ម_ត_ស_ទ_ធ_Bours_Neak_Samouth_Sothea_studio.wav
- /home/ubuntu/CHR/sound-engineer/jobs/ប_សន_គ_ស_ម_ត_ស_ទ_ធ_Bours_Neak_Samouth_Sothea/studio/work/session/ប_សន_គ_ស_ម_ត_ស_ទ_ធ_Bours_Neak_Samouth_Sothea_studio.scraft
