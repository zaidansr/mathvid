# Reviewer handoff and checks

Receive the original title, question and supplied solution; current narration/storyboard; generated speech and timings; captions; ManimGX source; final MP4; and mix settings. Review the finished artefacts, not merely the plan or another agent's assurance.

## Mathematical and spoken logic

Solve or independently verify the question before relying on the supplied solution. Check domains, units, signs, equality versus approximation, division by zero, extraneous roots, missing cases, and assumptions relevant to this particular question. Verify numerical results with calculation when helpful. Confirm the final answer answers the actual question. Distinguish an informal intuition from a proof.

Compare every spoken claim and shown equation with that verified reasoning. Check that simplification for the one-minute format has not changed a condition or made a false generalization. Listen to spoken mathematical terms, fractions, negatives and indices; a correct transcript does not prove correct pronunciation. Check captions against actual speech and visual symbols. Report any correction to the user-provided solution explicitly.

Check the reel description against the original problem and verified solution. Confirm the answer includes essential conditions, units, and all relevant cases, and that any key idea is supported by the solution and accurately reflects the reel. Check that the copy stays brief and that `reel-description.txt` matches the description delivered to the user.

## Render and audio

1. Run ManimGX inspection where supported, then view its storyboard and representative exported frames at phone scale. Check text bounds, legibility, label collisions, caption overlap, curve/axis alignment and colour consistency. Sampled layout checks alone do not certify the whole video.
2. Inspect motion around each equation transform and scene transition. Look for flicker, missing glyphs, unintended stale objects, jumps and black frames. Review the whole clip in playback if the environment supports it. Static frames cannot rule out temporal artefacts; state if playback could not be checked.
3. Listen through the mix if supported. Verify pronunciation, sentence endings, speech/music balance, clipping, clicks, fades and sync. If listening is unavailable, report this limitation; signal levels do not establish intelligibility.
4. Use ffprobe (or equivalent verified tooling) to confirm portrait dimensions, video and audio streams, frame rate, actual duration and decodability. Ensure the final spoken word is not truncated and the final answer has a readable hold. Check cues at the start, middle and end for accumulated drift. Flag target-duration overruns without blindly trimming the ending.

Return findings as `severity | timestamp or beat ID | evidence | owning role | requested fix`. Recheck corrected segments and downstream timing when narration changes. If no defects are found, report what was inspected and what was not; do not promise the video is artifact-free based on partial coverage.
