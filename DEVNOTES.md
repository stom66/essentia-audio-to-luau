
# DevNotes


Just a list of commands to copy-paste and save time with.

#### download all songs

```sh
python3 roblox_id_to_luau.py 77880172078468 142376088 87482792172761 129839967918512 101843316787835
```





#### Copy songData to project dir:

```sh
cp output/*.luau /mnt/c/projects/rblx-bab-test-rhythm-game/src/luau/shared/Data/SongData/
```

python3 roblox-id-to-luau.py 113047371246790 127815296704911 1837464821 1840222011 1840434670 1842286824 77824671936417 99445078556609 84167213533840



### Mazz advice

- Ignore anything over 5khz - washy bullshit, cymbols etc
- problem with the first one is the envelope for beat detection isn't short enough
- dont have random inputs - use patterns. eg, require user to press up-down-up-down, or left-left-right-left, and switch the pattern every. makes it feel more "musical" and varied even when they're just doing the same thing repeatedly
- double-notes - consider requiring the user to press multiple inputs at the same time 