# FramePicker
### FramePicker - Pick Your Frames from AI-Generated Videos
- For Unity Sprite Animation Asset Creation
- Process AI-Generated Short Video 

With FramePicker, you can **preview, select, crop, resize, and export** only the frames you need — all in one place.

## Main Workflow
1. **Load Video** → Click `[File]` to load an AI-generated video (max 500 frames).
2. **Create Collection** → Click `[+]` to make a new frame set.
3. **Set Destination** → Click any collection to mark it as **dst** (target for adding frames).
4. **Preview Frames** → Click `[Open in viewer]` to browse a collection as **src**.
5. **Add Frame** → In viewer, click `[Add to Selected Collection]` to copy current frame to **dst**.
6. **Delete Frame** → In viewer, click `[Delete from Viewing Collection]` to delete current frame from **src**.
7. **Edit Frame** → In viewer, click `[Crop]` or `[Resize]` to edit current frame.
8. **Export** → Select a collection, click `[Download]`, choose format (PNG recommended for Unity).

>  Note: You can only delete frames when **src == dst**.

## Limitations
- Maximum **500 frames** per video (to avoid memory issues)
- Only supports common video formats: MP4, MOV, AVI
- Cropping/resizing applies to **all frames** in the current `src` collection

## Docs
- [Detail Workflow](docs/detail_workflow.md)

## Update

---
> - #### Version 1.0.2 (2026.xx.xx)
> - `[NEW FEATURE]` Support loop playback of the Collection
> - `[NEW FEATURE]` Support flipping the frames in the Collection
> - `[NEW FEATURE]` Export the Collection as a single large image
> - `[NEW FEATURE]` Cut the length of the Collection based on the start and end frames
> - `[BUG FIXED]` Respect input frame index in frame viewer
> - #### Todo
> - `[TODO]` Import a frame from an image
---
> - #### Version 1.0.1 (2025.12.29)
> - `[NEW FEATURE]` `Play` a collection with target fps
> - `[NEW FEATURE]` Support creating a new collection by inheriting a source collection
> - `[NEW FEATURE]` Update ui icon
> - #### Todo
> - ~~`[TODO]` Export the Collection as a single large image~~
> - ~~`[TODO]` Support flipping the frames in the Collection~~
> - ~~`[TODO]` Crop the length of the Collection based on the start and end frames~~
> - `[TODO]` Import a Collection from an image folder
> - `[TODO]` Export the Collection as a video
> - ~~`[TODO]` Support loop playback of the Collection~~
---
> - #### Version 1.0.0 (2025.12.19)
> - `[NEW FEATURE]` `Decode` video as single frames
> - `[NEW FEATURE]` `Select` frames to a new collection
> - `[NEW FEATURE]` `Crop` all the frames in collection
> - `[NEW FEATURE]` `Resize` all the frames in collection
> - `[NEW FEATURE]` `Download` a collection as png or jpeg images
> - #### Todo
> - `[TODO]` Collection list width exception → fixed width
> - `[TODO]` The memory usage is too large and will increase dramatically based on frame copying → The collection only saving frame index
> - `[TODO]` Option Page → editable decoding frames
> - `[TODO]` Option Page → switchable memory performance modes
> - `[TODO]` Option Page → check for updates
> - `[TODO]` Option Page → update to a developing preemptive version
> - `[TODO]` → Interface beautification
> - ~~`[TODO]` → Play frames according to the set frame rate~~
> - `[TODO]` → Add test suites to test code
