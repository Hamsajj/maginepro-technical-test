import argparse
from boto3.exceptions import S3UploadFailedError
from utils import *


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
    parser.add_argument("input_file", help="input video file path")
    parser.add_argument("output_file",
                        help="desired output path for the resized video, will create directory if does not exist")
    parser.add_argument("bucket_name", help="s3 bucket name you want to upload to")
    parser.add_argument("bucket_key", help="s3 bucket key")
    parser.add_argument('--height', help="resize videos to match this height", type=int, default=120)
    parser.add_argument("-v", "--verbose", help="logs debug information", action="store_true")
    parser.add_argument("-r", "--replace", help="replace local file if already exists"
                                                " (NOTE: will replace object in s3 bucket regardless of this flag)",
                        action="store_true")
    return parser.parse_args()


def main(input_file: str, output_file: str, bucket_name: str, bucket_key: str, height: int, verbose=False,
         replace_if_exists=True):
    try:
        if not os.path.isfile(input_file):
            logging.error(f"input file not found: '{input_file}'.")
            return
        if not replace_if_exists and os.path.isfile(output_file):
            logging.error(f"output file already exists: '{output_file}.'")
            return

        resize_video(input_file, output_file, height=height, verbose=verbose)
        upload_to_s3(output_file, bucket_name, bucket_key)
        logging.info("finished successfully")
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] == "403":
            logging.error(f'access denied to s3 bucket {bucket_name} - {e}')
        else:
            logging.error(f'something went wrong with aws - {e}')
    except S3UploadFailedError as e:
        logging.error(f'could not upload the file to s3://{bucket_name}/{bucket_key}: {e}')
    except Exception as e:
        logging.error(f'something went wrong: {e}')


if __name__ == '__main__':
    args = init_arg_parser()
    init_logger(args.verbose)
    main(args.input_file, args.output_file, args.bucket_name, args.bucket_key, args.height, args.verbose, args.replace)
