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
$python main.py sample.mp4 out.mp4 bucketname resized_sample.mp4
```
To read more, run `main.py` with `--help`:
```sh
$python main.py --help
usage: main.py [-h] [--height HEIGHT] [-v] [-r] input_file output_file bucket_name bucket_key

This simple CLI, resizes a video and upload the output to a S3 bucket

positional arguments:
  input_file       input video file path
  output_file      desired output path for the resized video, will create directory if does not exist
  bucket_name      s3 bucket name you want to upload to
  bucket_key       s3 bucket key

options:
  -h, --help       show this help message and exit
  --height HEIGHT  resize videos to match this height
  -v, --verbose    logs debug information
  -r, --replace    replace local file if already exists (NOTE: will replace object in s3 bucket regardless of this flag)
```


