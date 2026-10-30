**English** | [Русский](README.md)

# Silero TTS Enhanced - Home Assistant Integration

A modern, UI-configurable Home Assistant integration for Silero TTS. No more YAML editing!

This integration connects directly to the **Silero TTS Enhanced Engine Add-on** and exposes it as a native Media Player / Voice Assistant TTS provider in Home Assistant.

## Features

- ⚙️ **Config Flow (UI):** Set up IPs, languages, voices, and sample rates entirely via the Home Assistant UI.
- 🗣️ **Voice Assistant Ready:** Fully compatible with Home Assistant's "Assist" feature.
- 🚀 **Asynchronous & Fast:** Uses non-blocking HTTP requests. No system freezes.
- 🔄 **Dynamic Model Discovery:** Automatically fetches the latest models, languages, and voices from the official Silero repository. No hardcoded lists!
- 🎯 **Context-Aware Selection:** Available voices and sample rates are filtered based on your selected model.
- 🛡️ **Fault Tolerant:** If GitHub is unavailable at startup, the integration uses safe defaults and allows manual model input.
- **Multi-language:** Supports `ru`, `en`, `de`, `es`, `fr`, `tt`, `uz`, `ua`, `multi`, and more.

## Installation via HACS

1. Ensure you have installed the companion Silero Add-on and it's running.
2. Open **HACS** -> **Integrations**.
3. Click the three dots (top right) -> **Custom repositories**.
4. Add this repository URL as an **Integration**.
5. Click **Download**, then **Restart Home Assistant**.

## Setup

1. Go to **Settings** -> **Devices & Services**.
2. Click **+ Add Integration** and search for `Silero TTS Enhanced`.
3. Follow the multi-step wizard:
   - Enter your Add-on Server IP (e.g., `http://192.168.1.114:8014`).
   - Select your preferred language.
   - Choose a model version.
   - Configure voice, sample rate, and pronunciation options.
4. Done! The integration will automatically fetch the latest available models from Silero.

## Usage in Automations

```yaml
service: tts.speak
target:
  entity_id: tts.silero_tts_enhanced
data:
  media_player_entity_id: media_player.living_room
  message: "Hello world, the smart home is ready."
  language: "en"
  options:
    model_id: "v3_en"
    voice: "en_24"
```

### Available Models and Speakers

The integration dynamically fetches models from the official [Silero Models repository](https://github.com/snakers4/silero-models). As of now, it supports:

| Language | Model Versions | Speakers |
| :-- | :-- | :-- |
| **Russian** | v5_ru, v5_5_ru, v5_6_ru, v4_ru, v3_1_ru | aidar, baya, kseniya, xenia, eugene, and more |
| **English** | v3_en, v3_en_indic | en_0, en_1, ..., en_117 |
| **German** | v3_de, thorsten_v2 | bernd_ungerer, eva_k, friedrich, hokuspokus, karlsson, thorsten |
| **Spanish** | v3_es, tux_v2 | es_0, es_1, es_2, tux |
| **French** | v3_fr, gilles_v2 | fr_0, fr_1, ..., fr_5, gilles |
| **Ukrainian** | v4_ua, v3_ua | mykyta |
| **Uzbek** | v4_uz, v3_uz | dilnavoz |
| **Tatar** | v3_tt | dilyara |
| **Mongolian** | v3_xal | erdni, delghir |
| **Multi-language** | multi_v2 | aidar, baya, kseniya, irina, ruslan, natasha, thorsten, tux, gilles, lj, dilyara |

*Note: New models are automatically available when Silero releases them. No integration update required!*

## How It Works

On every Home Assistant startup, the integration fetches the `models.yml` file from the official Silero Models repository in the background. This file contains up-to-date information about all available models, languages, voices, and supported sample rates.

Based on this data, dynamic lists are generated in the configuration interface, which allows:
- Using new models immediately after release
- Seeing only the voices and sample rates supported by the selected model
- Manually entering a model name if it hasn't been added to YAML yet

## Troubleshooting

### Integration doesn't load models

If you see only a basic list of models during setup, check:
- Internet availability on the Home Assistant server
- Home Assistant logs for `models.yml` loading errors
- If necessary, you can manually enter the model name via the "Custom value" option in the selector

### Playback errors

- Make sure the Silero TTS Enhanced add-on is running
- Verify the server URL is correct (must be accessible from the Home Assistant network)
- Check that the selected model and voice support the specified sample rate

## 📝 Acknowledgements & License

This project is an unofficial wrapper/integration. The core Text-to-Speech neural models are developed and owned by the Silero Team.
The models are published under the **CC BY-NC** (Non-Commercial) license. Please respect the authors' rights and use this integration strictly for personal, non-commercial purposes.
