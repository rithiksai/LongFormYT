"""Generate vertical images for YouTube Shorts using Stability.AI API."""

import os
import base64
import time
import requests
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()


def generate_images_for_short(
    visual_suggestions: list[str],
    output_dir: str,
    api_key: str = None,
    width: int = 768,
    height: int = 1344,
    engine_id: str = "stable-diffusion-xl-1024-v1-0",
) -> List[str]:
    """
    Generate vertical images for YouTube Shorts using Stability.AI.

    Args:
        visual_suggestions: List of image prompts from script generation
        output_dir: Directory to save generated images
        api_key: Stability.AI API key (defaults to STABILITY_API_KEY env var)
        width: Image width (default: 768 for 9:16 ratio)
        height: Image height (default: 1344 for 9:16 ratio)
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

    if not visual_suggestions:
        raise ValueError("No visual suggestions provided")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating {len(visual_suggestions)} images using Stability.AI...")
    print(f"  Resolution: {width}x{height} (9:16 vertical)")
    print(f"  Output: {output_dir}/")
    print()

    api_host = "https://api.stability.ai"
    generated_images = []

    # Generate image for each visual suggestion
    for i, prompt in enumerate(visual_suggestions, 1):
        if not prompt:
            print(f"  Image {i}/{len(visual_suggestions)}: Skipping empty prompt")
            continue

        # Truncate prompt for display
        prompt_preview = prompt[:60] + ("..." if len(prompt) > 60 else "")
        print(f"  Image {i}/{len(visual_suggestions)}: \"{prompt_preview}\"")

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
                            "text": prompt
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
                print(f"    Error: {error_msg}")

                # Check for rate limit
                if response.status_code == 429:
                    print("    Rate limit hit, waiting 60 seconds...")
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
                            "text_prompts": [{"text": prompt}],
                            "cfg_scale": 7,
                            "height": height,
                            "width": width,
                            "samples": 1,
                            "steps": 30
                        },
                    )

                    if response.status_code != 200:
                        print(f"    Retry failed: {response.status_code}")
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
                print(f"    Saved: {file_path}")

        except requests.exceptions.RequestException as e:
            print(f"    Network error: {e}")
            continue
        except Exception as e:
            print(f"    Error: {e}")
            continue

        # Small delay to avoid overwhelming the API
        time.sleep(0.5)

    print(f"\nGenerated {len(generated_images)}/{len(visual_suggestions)} images successfully")

    if len(generated_images) == 0:
        raise Exception("Failed to generate any images. Check API key and network connection.")

    return generated_images


if __name__ == "__main__":
    # Test with sample prompts
    test_prompts = [
        "Anime style close-up portrait of a determined warrior with glowing eyes",
        "Anime style vertical scene of a mystical forest with floating lights",
    ]

    try:
        images = generate_images_for_short(test_prompts, "output/test_images")
        print(f"\nTest successful! Generated {len(images)} images:")
        for img in images:
            print(f"  - {img}")
    except Exception as e:
        print(f"\nTest failed: {e}")
