from PIL import ImageTk, Image, ImageSequence
import tkinter as tk
import os
import time
import threading
import queue
import multiprocessing
import random

MIN_DELAY = 20
FALLBACK_DELAY = 100
DELAY_BETWEEN = 5000
MAX_WIDTH = 100000
MAX_HEIGHT = 100000

def decode_and_scale_gif(path, scale):
    frames = []
    delays = []

    gif = Image.open(path)

    for frame in ImageSequence.Iterator(gif):
        duration = frame.info.get("duration", FALLBACK_DELAY)

        frame = frame.convert("RGBA")
        new_size = (int(frame.width * scale), int(frame.height * scale))
        frame = frame.resize(new_size, Image.Resampling.LANCZOS)

        frames.append(frame)
        delays.append(duration)

    return frames, delays

def decode_openGif(root, path):
    window = tk.Toplevel()
    window.title("gif")

    label = tk.Label(window)
    label.pack()

    with Image.open(path) as img:
        scale = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height, 1)
    
    pool = multiprocessing.Pool(processes=1)
    future = pool.apply_async(decode_and_scale_gif, (path, scale))

    #frames, delays = future.get()

    frames = []
    delays = []
    photoframes =  []
    frame_index = 0




    def poll_frames():
        nonlocal photoframes, delays

        if future.ready():
            frames, delays = future.get()
            photoframes = [ImageTk.PhotoImage(f) for f in frames]
            start_animation()
        else:
            window.after(50, poll_frames)

    def start_animation():
        nonlocal frame_index

        if not window.winfo_exists() or not photoframes:
            return
        label.config(image=photoframes[frame_index])
        frame_index = (frame_index + 1 ) % len(photoframes)
        window.after(delays[frame_index], update_animation)

    def update_animation():
        nonlocal frame_index

        if not window.winfo_exists():
            return
        
        label.config(image=photoframes[frame_index])
        frame_index = (frame_index + 1 ) % len(photoframes)
        window.after(delays[frame_index], update_animation)

    window.after(0, poll_frames)
    window.overrideredirect(True)
    make_draggable(window)
    make_close_on_LClick(window)
    return window

def scaled_openGif(root, path):
    window = tk.Toplevel()
    window.title("gif")

    label = tk.Label(window)
    label.pack()

    window.overrideredirect(True)
    make_draggable(window)
    make_close_on_LClick(window)

    gif = Image.open(path)
    frames = ImageSequence.Iterator(gif)

    scale = min(MAX_WIDTH / gif.width, MAX_HEIGHT / gif.height, 1)

    current_frame = None

    def next_frame():
        nonlocal  current_frame

        try:
            #frame= next(frames)
            gif.seek(gif.tell() +1)
        #except StopIteration:
        except EOFError:
            gif.seek(0)
            #frame = next(frames)
        frame = gif.copy()

        frame = frame.convert("RGBA")
        new_size = (int(frame.width * scale), int(frame.height * scale))
        frame = frame.resize(new_size, Image.Resampling.LANCZOS)

        current_frame = ImageTk.PhotoImage(frame)
        label.config(image=current_frame)

        delay = frame.info.get("duration", 100)
        window.after(max(delay,20), next_frame)

    window.after(0, next_frame)


    return window

def make_draggable(window):
    window._drag_start_x = 0
    window._drag_start_y = 0

    def start_drag(event):
        window._drag_start_x = event.x
        window._drag_start_y = event.y

    def do_drag(event):
        x = window.winfo_x() + (event.x - window._drag_start_x)
        y = window.winfo_y() + (event.y - window._drag_start_y)
        window.geometry(f"+{x}+{y}")

    window.bind("<Button-3>", start_drag)
    window.bind("<B3-Motion>", do_drag)
            
def make_close_on_LClick(window):

    def close_window(event):
        window.destroy()

    window.bind("<Button-1>",  close_window)

def openImage(root, path):
    window = tk.Toplevel(root)
    img = Image.open(path)
    photo = ImageTk.PhotoImage(img)
    window.title(path)
    window.geometry(f"{img.width}x{img.height}+-2500+-350")
    label = tk.Label(window, image=photo)
    label.image = photo  # keep reference
    label.pack()
    window.protocol("WM_DELETE_WINDOW", lambda: on_close(root, window))

def openGif(root, path):
    window = tk.Toplevel(root)
    window.title(path)

    window.update_idletasks()

    label  = tk.Label(window)
    label.pack()

    frames = []
    delays = []
    frame_index=0

    frame_queue = queue.Queue(maxsize=10)
    stop_flag = threading.Event()

    def loader():
        gif = Image.open(path)
        for frame  in ImageSequence.Iterator(gif):
            if stop_flag.is_set():
                break

            duration = frame.info.get("duration", FALLBACK_DELAY)
            frame_queue.put((frame.copy(), max(duration, MIN_DELAY)))

            time.sleep(.005)

    def process_queue():
        if not window.winfo_exists():
            stop_flag.set()
            return
        for _ in range(2):
            try:
                while True:
                    frame, delay = frame_queue.get_nowait()
                    frames.append(ImageTk.PhotoImage(frame))
                    delays.append(delay)
            except queue.Empty:
                pass

        window.after(10, process_queue)

    def update_animation():
        nonlocal frame_index

        if not window.winfo_exists() or not frames:
            return
        
        label.config(image=frames[frame_index])
        current_delay = delays[frame_index]

        frame_index = (frame_index + 1) % len(frames)
            
        window.after(current_delay, update_animation)

    threading.Thread(target=loader, daemon=True).start()
    window.after(0, process_queue)
    window.after(0, update_animation)
    window.overrideredirect(True)
    make_draggable(window)
    make_close_on_LClick(window)
    return window

def on_close(root, window):
    window.destroy()

    if not root.winfo_children():
        root.quit()

def readFromFolder(root, path):
    if not os.path.isdir(path):
        raise ValueError(f"Invalid folder: {path}")
    
    gif_files =  sorted(
        os.path.join(path, f)
        for f  in os.listdir(path)
        if f.lower().endswith(".gif")
    )

    index = 0
    count = 0
    last_spawn_time = time.time()


    if True:
        random.shuffle(gif_files)

    def spawn_next():
        nonlocal index, count, last_spawn_time
        if index >= len(gif_files):
            return
        start = time.time()
        
        #openGif(root, gif_files[index])
        scaled_openGif(root, gif_files[index])
        count += 1
        index += 1

        end = time.time()
        spawn_duration = end - start
        delta = end - last_spawn_time

        print(f"Spawned: {count} | Time to spawn: {spawn_duration:.4f}s | Delta since last: {delta:.4f}s")

        last_spawn_time = end

        root.after(DELAY_BETWEEN, spawn_next)

    spawn_next()
    
if __name__ == "__main__":
    root = tk.Tk()
    root.iconify()


    readFromFolder(root, "gifs1")

    root.mainloop()