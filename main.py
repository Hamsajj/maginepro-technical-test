import argparse
from queue import Queue

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
    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument('-i', "--input-file", help="input video file path", )
    input_group.add_argument('-I', "--input-directory", help="input directory including only video files")

    output_group = parser.add_mutually_exclusive_group(required=True)

    output_group.add_argument('-o', "--output-file", help="input video file path", )
    output_group.add_argument('-O', "--output-directory", help="output directory, required if the input is a directory")

    # parser.add_argument("-o", "--output-file", required=True,
    #                     help="desired output path for the resized video, will create directory if does not exist")
    parser.add_argument("-b", "--bucket-name", required=True, help="s3 bucket name you want to upload to")
    parser.add_argument("-k", "--bucket-key", help="s3 bucket key - "
                                                   "not required if working with directory "
                                                   "(object key will be the same as filename in that case")
    parser.add_argument('--height', help="resize videos to match this height", type=int, default=120)
    parser.add_argument("-v", "--verbose", help="logs debug information", action="store_true")
    parser.add_argument("-r", "--replace", help="replace local file if already exists"
                                                " (NOTE: will replace object in s3 bucket regardless of this flag)",
                        action="store_true")
    args = parser.parse_args()
    if bool(args.input_directory) != bool(args.output_directory):
        parser.error("if one of --input-directory or --output-directory is given, the other one should be present too")

    if bool(args.input_file) != bool(args.output_file):
        parser.error("if one of --input-file or --output-file is given, the other one should be present too")

    if args.input_file is not None and args.bucket_key is None:
        parser.error("--bucket-key should be provided when using a file as input")
    return args


def process_video(input_file: str, output_file: str, height: int, verbose=False,
                  replace_if_exists=True) -> str:
    try:
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"input file not found: '{input_file}'.")
        if not replace_if_exists and os.path.isfile(output_file):
            raise FileExistsError(f"output file already exists: '{output_file}.'")
        resize_video(input_file, output_file, height=height, verbose=verbose)
        logging.info("finished successfully")
        return output_file
    except Exception as e:
        logging.error(f'something went wrong: {e}')
        raise e


def process_file(input_file: str, output_file: str, bucket_name: str, bucket_key: str, height: int, verbose=False,
                 replace_if_exists=True):
    try:
        process_video(input_file, output_file, height=height, verbose=verbose, replace_if_exists=replace_if_exists)
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
        logging.error(e)


def process_directory(input_dir: str, output_dir: str, bucket_name: str, height: int, verbose=False,
                      replace_if_exists=True):
    logging.info(f'processing all files in directory {input_dir}')
    for filename in os.listdir(input_dir):
        f = os.path.join(input_dir, filename)
        if not os.path.isfile(f):
            continue
        output_file = os.path.join(output_dir, filename)
        process_file(f, output_file, bucket_name, filename, height, verbose, replace_if_exists)


if __name__ == '__main__':
    args = init_arg_parser()
    init_logger(args.verbose)

    if args.input_directory:
        process_directory(args.input_directory, args.output_directory, args.bucket_name,
                          args.height, args.verbose, args.replace)
    else:
        process_file(args.input_file, args.output_file, args.bucket_name, args.bucket_key, args.height, args.verbose,
                     args.replace)
    logging.info("DONE")
