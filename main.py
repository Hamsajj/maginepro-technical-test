import argparse
import sys
import threading
from queue import Queue

from boto3.exceptions import S3UploadFailedError
from utils import *
from workers import *


def init_logger(verbose: bool = False):
    if not verbose:
        import warnings
        warnings.filterwarnings("ignore")
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
        level=logging.DEBUG if verbose else logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')


def init_arg_parser():
    parser = argparse.ArgumentParser(
        description='This simple CLI, resizes a video and upload the output to a S3 bucket',
        add_help=True)
    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument('-i', "--input-file", help="input video file path", )
    input_group.add_argument('-I', "--input-directory", help="input directory including only video files")

    parser.add_argument('-o', "--output-directory", help="output directory", required=True)

    parser.add_argument("-b", "--bucket-name", required=True, help="s3 bucket name you want to upload to")

    parser.add_argument('--height', help="resize videos to match this height", type=int, default=120)
    parser.add_argument("-v", "--verbose", help="logs debug information", action="store_true")
    parser.add_argument("-r", "--replace", help="replace local file if already exists"
                                                " (NOTE: will replace object in s3 bucket regardless of this flag)",
                        action="store_true")
    parser.add_argument("-t", "--threads", type=int,
                        help="number of threads working on processing and uploading video files,"
                             " 2 means 2 thread will work on processing and 2 will work on uploading",
                        default=2)
    return parser.parse_args()


def get_all_files_from_directory(directory: str) -> list[str]:
    files = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if not os.path.isfile(f):
            continue
        files.append(f)
    return files


if __name__ == '__main__':
    args = init_arg_parser()
    threads_number = args.threads
    to_process = Queue()
    to_upload = Queue()
    init_logger(args.verbose)
    files_to_process = []
    if args.input_directory:
        files_to_process = get_all_files_from_directory(args.input_directory)
    else:
        files_to_process.append(args.input_file)
    if len(files_to_process) == 0:
        logging.info("No file to process!")
    add_files_to_process_queue(files_to_process, to_process, threads_number)
    for i in range(threads_number):
        logging.debug(f"started thread {i + 1} for video processing")
        t = threading.Thread(target=video_process_worker,
                             args=(
                                 to_process, to_upload, args.output_directory, args.height, args.verbose,
                                 args.replace,))
        t.start()
    for i in range(threads_number):
        logging.debug(f"started thread {i + 1} for video uploading")
        t = threading.Thread(target=video_upload_worker,
                             args=(to_upload, args.bucket_name,))
        t.start()

    to_process.join()
    to_upload.join()
    logging.info("DONE")
