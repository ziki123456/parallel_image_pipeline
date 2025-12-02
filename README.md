# Parallel Image Processing Pipeline

Multithreaded Python application for processing images in parallel using a loader–worker–saver architecture.

## Overview

This project processes all images in the **input/** directory using multiple worker threads, applies image transformations, and saves the results into the **output/** directory.

The application demonstrates real-world parallelism, synchronization, and safe communication between threads using Python's `queue.Queue` and locks.

## Features

* Parallel image processing
* Configurable number of worker threads
* Automatic folder handling
* Thread-safe communication via queues
* Resize and grayscale filters
* Safe worker shutdown using sentinels

## Project Structure

```
PV_Rocnikova_Prace/
├── bin/
├── doc/
├── input/
├── output/
├── src/
│   ├── main.py
│   └── pipeline/
│       ├── __init__.py
│       ├── config.py
│       ├── loader.py
│       ├── processor.py
│       └── saver.py
└── requirements.txt
```

## Requirements

Install required libraries:

```
pip install -r requirements.txt
```

## How to Run

1. Place `.jpg` or `.png` images inside the **input/** directory.
2. Run the application:

```
python src/main.py
```

3. Processed images will appear in the **output/** directory.

## Configuration

The `Config` class in `config.py` allows adjustment of:

* Input folder
* Output folder
* Number of workers
* Resize dimensions
* Whether to apply grayscale

Example:

class Config:
pass

```
python
Config(
    input_dir="input",
    output_dir="output",
    num_workers=3,
    resize_to=(800, 800),
    grayscale=True
)
```

## How It Works

* **loader_thread** reads filenames and pushes them into a queue.
* **worker threads** take filenames, load and process images, and push processed results into another queue.
* **saver_thread** takes processed images and writes them to disk.

Queues ensure safe communication between threads.

## Thread Safety

* Uses `queue.Queue` (thread-safe) for communication.
* Uses a shared `active_workers` counter protected by a lock.
* Uses sentinel values (`None`) to cleanly terminate workers.

## Output

Processed images are saved using the original filename, transformed according to configuration.

## Author

Tadeáš — PV Ročníková Práce
