# Parallel Image Processing Pipeline

Multithreaded Python application for processing images in parallel using a loader–worker–saver architecture.

## Overview

This project processes all images in the **input/** directory using multiple worker threads, applies image transformations, and saves the results into the **output/** directory.

The application demonstrates real-world parallelism, synchronization, and safe communication between threads using Python's `queue.Queue` and locks.

## Features

* Parallel image processing
* Automatic or manual worker thread selection
* Automatic folder handling
* Thread-safe communication via queues
* Resize and grayscale filters
* Safe worker shutdown using sentinels
* Logging system (logs/app.log)
* Modular loader → processor → saver architecture

## Project Structure

```
PV_Rocnikova_Prace/
├── bin/
├── doc/
├── input/
├── output/
├── logs/
│   └── app.log
├── src/
│   ├── main.py
│   └── pipeline/
│       ├── __init__.py
│       ├── config.py
│       ├── loader.py
│       ├── processor.py
│       ├── saver.py
│       └── logger_setup.py
└── requirements.txt
```

## Requirements

Install required libraries:

```
pip install -r requirements.txt
```

If this does not work, try:

```
python -m pip install pillow
python -m pip install pyyaml
```

## How to Run

1. Place `.jpg` or `.png` images inside the **input/** directory.
2. Run the application:

```
python src/main.py
```

3. Processed images will appear in the **output/** directory.
4. Logs will appear in **logs/app.log**.

## Configuration

The `Config` class in `config.py` allows adjustment of:

* Input folder
* Output folder
* Worker thread configuration
* Resize dimensions
* Grayscale on/off
* Logging on/off

### Automatic Worker Thread Calculation

If `auto_threads = True`, the program uses:

```
num_workers = min(cpu_count() * 2, number_of_images)
```

### Example Configuration

```python
class Config:
    input_dir = "input"
    output_dir = "output"

    auto_threads = True
    num_workers = 3

    resize_to = (800, 800)
    grayscale = True

    logging_enabled = True
```

## How It Works

* **loader_thread**  
  Reads filenames from the input folder and pushes them into a queue.  
  Sends a sentinel value (`None`) when finished.

* **worker threads**  
  Take filenames from the queue, load images, apply transformations, and push results into the save queue.

* **saver_thread**  
  Saves processed images to the output directory.  
  Terminates after receiving the required number of sentinels.

Queues ensure safe communication between all parts of the pipeline.

## Thread Safety

* Uses `queue.Queue` (thread-safe) for communication.
* Shared counters protected by locks.
* Sentinels (`None`) ensure clean worker shutdown without race conditions.

## Logging System

All events are recorded in:

```
logs/app.log
```

(Worker activity, errors, warnings, file load/save actions, pipeline status updates.)

## Output

Processed images are saved using the original filenames, resized and/or converted to grayscale according to configuration.

## Author

Tadeáš — PV Ročníková Práce
