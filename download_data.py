import configparser
import os
import shutil
import subprocess


def download_files(config_folder,
                   raw_data_folder,
                   log_file):
    dataset_folders = list()
    list_files = list()

    with open(log_file, 'w') as f:
        for folder in os.listdir(config_folder):
            complete_folder = os.path.join(config_folder, folder)
            if os.path.isdir(complete_folder):  # It could be a .csv
                dataset_folders.append(folder)
                config_file = os.path.join(complete_folder, 'config.ini')
                list_files.append(config_file)
                config = configparser.ConfigParser()
                config.read(config_file)
                try:
                    data_url = config['info']['data_url']
                    data_download = os.path.split(config['info']['data_url'])[-1]
                    data_name = config['info']['name']
                    f.write(''.join([data_url, '\n']))
                    download_filename = os.path.join(complete_folder, data_download)
                    final_filename = os.path.join(complete_folder, data_name)
                    if not os.path.isfile(final_filename):
                        # Download file
                        bash_command = ['wget', '-nc', data_url, '-O', download_filename]
                        subprocess.run(bash_command)
                        # Extract data if necessary
                        if '.tar.gz' in data_download:
                            extract_tar(complete_folder=complete_folder,
                                        tar_file=data_download,
                                        data_name=data_name)
                        elif data_name != data_download:
                            os.rename(download_filename,
                                      final_filename)
                    else:
                        # print('Dataset', data_name, 'already downloaded')
                        pass
                    # Copy file to raw data folder
                    final_filename_2 = os.path.join(raw_data_folder, data_name)
                    shutil.copyfile(final_filename, final_filename_2)
                except Exception as e:
                    print(e)


def extract_tar(complete_folder, tar_file, data_name):
    """
    Extract tar.gz file and get the data.
    :param tar_file:
    :return:
    """
    files_folder = os.listdir(complete_folder)
    tar_file_path = os.path.join(complete_folder, tar_file)
    bash_command = ['tar', 'xzf', tar_file_path, '-C', complete_folder]
    subprocess.run(bash_command)
    new_files_folder = os.listdir(complete_folder)
    for f in new_files_folder:
        if f not in files_folder:  # Extracted file or folder
            if data_name == f:  # It is the file we were expecting
                break
            elif os.path.isdir(f):  # It is a folder
                subfolder_path = os.path.join(complete_folder, f)
                files_in_folder = os.listdir(subfolder_path)
                for f_s in files_in_folder:
                    if data_name == f_s:
                        shutil.move(os.path.join(subfolder_path, data_name),
                                    os.path.join(complete_folder, data_name))
                        shutil.rmtree(subfolder_path)
                        os.remove(tar_file_path)
                        break


def remove_files(config_folder):
    """
    Remove files from configuration folders.
    """
    for folder in os.listdir(config_folder):
        complete_folder = os.path.join(config_folder, folder)
        if os.path.isdir(complete_folder):  # It could be a .csv
            files = os.listdir(complete_folder)
            for file in files:
                if '.ini' not in file:
                    os.remove(os.path.join(complete_folder, file))


def check_folder(folder):
    """
    Create folder is necessary.

    :param str folder:
    """
    if not os.path.isdir(folder):
        os.mkdir(folder)


def remove_folder(folder):
    """
    Remove folder if it exists.

    :param str folder:
    """
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)


if __name__ == '__main__':
    # config_folders = ['datafiles/classification/', 'datafiles/regression/']
    config_folders = ['datafiles/classification/']
    log_file = 'logs/db.txt'
    raw_data_folder = 'raw_data'

    # Remove and create folder, for a fresh raw data
    remove_folder(raw_data_folder)
    check_folder(raw_data_folder)

    for config_folder in config_folders:
        data_type = config_folder.split('/')[1]
        raw_folder = os.path.join(raw_data_folder, data_type)
        check_folder(raw_folder)

        # remove_files(config_folder)
        download_files(config_folder=config_folder,
                       raw_data_folder=raw_folder,
                       log_file=log_file)
