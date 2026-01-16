"""Generate images from script using Stability.AI API."""

import os
import base64
import time
import requests
from pathlib import Path
from typing import List
from dotenv import load_dotenv
load_dotenv()


def generate_images_from_script(
    script_data: dict,
    output_dir: str = "assets/photos",
    api_key: str = None,
    width: int = 1344,
    height: int = 768,
    engine_id: str = "stable-diffusion-xl-1024-v1-0",
) -> List[str]:
    """
    Generate images for each scene using Stability.AI.

    Args:
        script_data: Script JSON with scenes array
        output_dir: Directory to save generated images
        api_key: Stability.AI API key (defaults to STABILITY_API_KEY env var)
        width: Image width (default: 1344 for 16:9 ratio)
        height: Image height (default: 768 for 16:9 ratio)
        engine_id: Stability.AI engine to use

    Returns:
        List of paths to generated images

    Raises:
        Exception: If API request fails or API key is missing
    """
    # Get API key from parameter or environment
    if api_key is None:
        api_key = os.environ.get("STABILITY_API_KEY")

    if not api_key:
        raise Exception(
            "Missing STABILITY_API_KEY. "
            "Set it in your .env file or pass as parameter."
        )

    # Extract scenes from script
    scenes = script_data.get("scenes", [])
    if not scenes:
        raise ValueError("Script data has no scenes")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating {len(scenes)} images using Stability.AI...")
    print(f"  Resolution: {width}x{height}")
    print(f"  Output: {output_dir}/")
    print()

    api_host = "https://api.stability.ai"
    generated_images = []

    # Generate image for each scene
    for i, scene in enumerate(scenes, 1):
        visual_suggestion = scene.get("visual_suggestion", "")

        if not visual_suggestion:
            print(f"  Scene {i}/{len(scenes)}: ⚠️  No visual suggestion, skipping")
            continue

        # Truncate prompt for display
        prompt_preview = visual_suggestion[:60] + ("..." if len(visual_suggestion) > 60 else "")
        print(f"  Scene {i}/{len(scenes)}: \"{prompt_preview}\"")

        # Make API request
        try:
            response = requests.post(
                f"{api_host}/v1/generation/{engine_id}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "text_prompts": [
                        {
                            "text": visual_suggestion
                        }
                    ],
                    "cfg_scale": 7,
                    "height": height,
                    "width": width,
                    "samples": 1,
                    "steps": 30
                },
            )

            # Handle API errors
            if response.status_code != 200:
                error_msg = f"API Error {response.status_code}: {response.text}"
                print(f"    ❌ {error_msg}")

                # Check for rate limit
                if response.status_code == 429:
                    print("    ⏳ Rate limit hit, waiting 60 seconds...")
                    time.sleep(60)
                    # Retry once
                    response = requests.post(
                        f"{api_host}/v1/generation/{engine_id}/text-to-image",
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        },
                        json={
                            "text_prompts": [{"text": visual_suggestion}],
                            "cfg_scale": 7,
                            "height": height,
                            "width": width,
                            "samples": 1,
                            "steps": 30
                        },
                    )

                    if response.status_code != 200:
                        print(f"    ❌ Retry failed: {response.status_code}")
                        continue
                else:
                    continue

            # Parse response and save image
            data = response.json()

            for artifact in data["artifacts"]:
                img_bytes = base64.b64decode(artifact["base64"])

                # Save with zero-padded numbering (01.png, 02.png, etc.)
                file_path = output_path / f"{i:02d}.png"

                with open(file_path, "wb") as f:
                    f.write(img_bytes)

                generated_images.append(str(file_path))
                print(f"    ✓ Saved → {file_path}")

        except requests.exceptions.RequestException as e:
            print(f"    ❌ Network error: {e}")
            continue
        except Exception as e:
            print(f"    ❌ Error: {e}")
            continue

        # Small delay to avoid overwhelming the API
        time.sleep(0.5)

    print(f"\n✅ Generated {len(generated_images)}/{len(scenes)} images successfully")

    if len(generated_images) == 0:
        raise Exception("Failed to generate any images. Check API key and network connection.")

    return generated_images


if __name__ == "__main__":
    # Test with a simple script
    test_script = {
        "script": "Test image generation",
        "duration_estimate": 12,
        "scenes": [
            {
                "timestamp": "0:00",
                "narration": "Test scene 1",
                "visual_suggestion": "Close-up photo of Naruto's face with determination in his eyes"
            },
            {
                "timestamp": "0:04",
                "narration": "Test scene 2",
                "visual_suggestion": "Landscape showing the Hidden Leaf Village at sunset with orange sky"
            }
        ]
    }

    try:
        images = generate_images_from_script(test_script, "assets/test_photos")
        print(f"\nTest successful! Generated {len(images)} images:")
        for img in images:
            print(f"  - {img}")
    except Exception as e:
        print(f"\nTest failed: {e}")
