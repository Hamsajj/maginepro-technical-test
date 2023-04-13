from queue import Queue

from boto3.exceptions import S3UploadFailedError

from utils import *

END_OF_QUEUE = object()


def add_files_to_process_queue(files: list[str], to_process_queue: Queue, num_threads: int):
    [to_process_queue.put(f) for f in files]
    # need to add end of queue for each thread working on it
    # that's the main reason why the number of threads working on upload vs process are equal
    [to_process_queue.put(END_OF_QUEUE) for i in range(num_threads)]


def video_process_worker(process_queue: Queue, upload_queue: Queue, output_dir: str, height: int, verbose=False,
                         replace_if_exists=True):
    while True:
        file_to_process = process_queue.get()
        if file_to_process is END_OF_QUEUE:
            process_queue.task_done()
            upload_queue.put(END_OF_QUEUE)
            logging.info("process queue done")
            break
        file_name = os.path.basename(file_to_process)
        output_file = os.path.join(output_dir, file_name)
        created_file = process_video(file_to_process, output_file, height, verbose, replace_if_exists)
        upload_queue.put(created_file)
        process_queue.task_done()


def video_upload_worker(upload_queue: Queue, bucket_name: str):
    while True:
        file_to_upload = upload_queue.get()
        if file_to_upload is END_OF_QUEUE:
            upload_queue.task_done()
            logging.info("upload queue done")
            break
        file_name = os.path.basename(file_to_upload)
        upload_to_s3(file_to_upload, bucket_name, file_name)
        upload_queue.task_done()


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
