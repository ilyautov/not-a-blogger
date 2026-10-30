# Key frame: seed sweep on 9-frame clips

- **Purpose:** find a good look for the hero and a good composition cheaply, before expensive long shots. A 9-frame
  t2v clip is generated on several seeds; the best frame becomes the i2v input.
- **Where tested:** LTX-2 locally, `ltx-2-mlx generate --distilled -H 1024 -W 576 -f 9 --seed $s`.
- **Status:** proven on 1 probe.

## Prompt

```text
{character passport}, {pose and object in hand}, {place}, {light}, realistic cinematic film still, 35mm photo,
medium shot from the waist up, static camera
```

Sweep:

```bash
for s in 1 2 3 5 8 13; do
  # check the prompt-input and output-path flags against `ltx-2-mlx generate --help` for your version
  ltx-2-mlx generate --distilled -H 1024 -W 576 -f 9 --seed "$s" ...
done
```

Take the middle frame of each clip, put them all on one contact sheet and pick by eye.

## Why

9 frames compute many times faster than a full shot, yet the hero's look and the light are already visible. A chosen
frame used as i2v input fixes the face and composition better than any text. The words `film still` and `35mm
photo` set a photographic look; they were tested only in this wording.

## Pitfalls

- A seed is deterministic only at the same size, frame count and model version. Changed `-f` or the model? Sweep
  again.
- Do not pick from one frame at a time: look at the contact sheet of all seeds at once, otherwise the first decent
  option seems best.
- If the face drifts on every seed, the problem is the passport, not the seed. Cut the small details (see the
  neighbouring prompt).
