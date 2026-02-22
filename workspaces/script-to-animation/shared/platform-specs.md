# Platform Specifications

Resolution, duration, and format constraints for each platform. Agents reference this to ensure scripts and specs fit the target format.

---

## Active Platform

This workspace is configured for **{{PRIMARY_PLATFORM}}** with a target duration of **{{TARGET_DURATION}}**.

---

## TikTok / Reels (Vertical Short-Form)

| Property | Value |
|----------|-------|
| Resolution | 1080 x 1920 (9:16) |
| FPS | 30 |
| Duration sweet spot | 45-60 seconds |
| Duration range | 30-90 seconds |
| Export format | MP4, H.264 |
| Max file size | 287 MB (TikTok), 250 MB (Reels) |

**Safe zones:**
- Top 15% -- platform UI (username, description) overlaps here
- Bottom 10% -- navigation bar overlaps here
- Keep critical content in the center 75% of the frame

**Text rules:**
- Minimum text size: 36px at 1080 width
- Maximum 3 lines of text visible at once
- High contrast required (dark text on light, or light text on dark)

---

## YouTube (Horizontal Long-Form)

| Property | Value |
|----------|-------|
| Resolution | 1920 x 1080 (16:9) |
| FPS | 30 |
| Duration sweet spot | 5-8 minutes |
| Duration range | 3-15 minutes |
| Export format | MP4, H.264 |
| Max file size | 256 GB |

**Safe zones:**
- Minimal. YouTube does not overlay UI on the video itself.
- Bottom 10% -- progress bar and controls appear on hover
- Keep subtitles above the bottom 15%

**Text rules:**
- Minimum text size: 24px at 1080 height
- More text density is acceptable than short-form
- Code snippets are readable at this resolution if kept to 20 lines or fewer

---

## YouTube Shorts (Vertical Short-Form)

| Property | Value |
|----------|-------|
| Resolution | 1080 x 1920 (9:16) |
| FPS | 30 |
| Duration sweet spot | 30-45 seconds |
| Duration range | 15-60 seconds |
| Export format | MP4, H.264 |

Same safe zone rules as TikTok/Reels.

---

## Cross-Platform Notes

If producing for multiple platforms:
- Author the vertical (9:16) version first. It is more constrained.
- Horizontal versions can use the extra width for side-by-side layouts.
- The script stays the same. The spec changes layout and timing to fit the format.
- Maintain separate spec files per platform: `[slug]-spec-vertical.md` and `[slug]-spec-horizontal.md`.
