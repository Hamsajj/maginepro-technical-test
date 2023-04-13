# MaginePro Technical Test
This is a simple Python script that processes a video file and uploads it to an S3 bucket.
Video process is a simple resizing for now.

### Prerequisites
#### ffmpeg
The code uses python package [moviepy]() which uses ffmpeg under the hood for the video processing tasks.
You can download it [here](https://ffmpeg.org/download.html). 

You can also install it using `sudo apt install ffmpeg` on ubuntu, or `brew install ffmpeg` on mcOS with homebrew.

I could use `ffmpeg` directly instead of `moviepy`. It would probably lead to an increase in processing speed. But it was a tradeoff between speed and ease of development and readibility and for this small test I chose `moviepy`

#### AWS
you need to have an aws IAM user with write access to the desired s3 bucket. Set the credentials and access keys of the user in `~/.aws/credentials` (or the equivalent file if on windows)

#### Python
Install python3, then run the following command to install requirements for this script:
```
pip install -r requirements.txt
```

### Run
If you want to resize video 'sample.mp4' and write the output to local file 'out.mp4' and upload to it to bucket `bucketname` with key `resized_sample.mp4` run the following command:
```sh
$python main.py -I ./tests/files/ -o out -b bucketname
```
To read more, run `main.py` with `--help`:
```sh
$python main.py --help
usage: main.py [-h] (-i INPUT_FILE | -I INPUT_DIRECTORY) -o OUTPUT_DIRECTORY -b BUCKET_NAME [--height HEIGHT] [-v] [-r] [-t THREADS]

This simple CLI, resizes a video and upload the output to a S3 bucket

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        input video file path
  -I INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
                        input directory including only video files
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        output directory
  -b BUCKET_NAME, --bucket-name BUCKET_NAME
                        s3 bucket name you want to upload to
  --height HEIGHT       resize videos to match this height
  -v, --verbose         logs debug information
  -r, --replace         replace local file if already exists (NOTE: will replace object in s3 bucket regardless of this flag)
  -t THREADS, --threads THREADS
                        number of threads working on processing and uploading video files, 2 means 2 thread will work on processing and 2 will work on uploading

```

This script works parallely on processing and uploading videos. 
A pool of threads work on files that need to be processed and another thread works on uploading processed videos.
by default 2 threads is created for processing and 2 others for uploading. You can change this by `--threads`


### Version

- [v1.0](https://github.com/Hamsajj/maginepro-technical-test/tree/v1.0): includes only main part of challenge
- [v1.1](https://github.com/Hamsajj/maginepro-technical-test/tree/v1.1): includes multi-thread support of processing all video files in a directory