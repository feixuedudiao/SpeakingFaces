import os
import glob
import argparse
import cv2
from speakingfacespy.imtools import make_dir
import scipy.io.wavfile

def extract_frame(audio_trim_filename, duration, data_path, stream_id):
    
    video_to_extract_filename  = '_'.join(audio_trim_filename.split('_')[:-1])+'_{}.avi'.format(stream_id)
    opt = 'thr' if stream_id == 1 else 'rgb'  
    video_to_extract_filepath = data_path + opt+ '_video_cmd' + os.path.sep + video_to_extract_filename
    print('[INFO] accessing a video file:'+ video_to_extract_filepath)
    extracted_images_dir = data_path + opt+ '_image_cmd'+ os.path.sep
    
    cap =  cv2.VideoCapture(video_to_extract_filepath)
    max_num_frames = int(duration*28)
    frame_id=1
    while(cap.isOpened() and frame_id <= max_num_frames):
        ret, frame = cap.read()
        if ret == False:
            break
        extracted_image_filename = '_'.join(audio_trim_filename.split('_')[:-1])+'_{}_{}.png'.format(frame_id, stream_id)
        extracted_image_filepath = extracted_images_dir+extracted_image_filename
        if not os.path.exists(extracted_image_filepath):
            if frame_id%10 == 0:
                print('[INFO] saving an extracted frame: '+ extracted_image_filepath)
            cv2.imwrite(extracted_image_filepath, frame)
        frame_id+=1
    
    cap.release()
    cv2.destroyAllWindows()
    print('[INFO] finished extracting frames')
    

def extract_frames_by_sub_trial(dataset_path, set_name, sub_id, trial_id):
    #assuming every trial has mic1_audio_cmd_trim folder
    print("[INFO] extract frames from videos by commands for sub_id = {}, trial_id = {}".format(sub_id, trial_id))
    data_path = '{}{}_data{}sub_{}{}trial_{}{}'.format(
        dataset_path, set_name, os.path.sep, sub_id, 
        os.path.sep, trial_id, os.path.sep)
    
    audio_trim_filepaths = glob.glob(data_path +'mic1_audio_cmd_trim'+os.path.sep+'*.wav')
    make_dir(data_path+'thr_image_cmd/')
    make_dir(data_path+'rgb_image_cmd/')
    print(data_path +'mic1_audio_cmd_trim'+os.path.sep+'*.wav')
    for audio_trim_filepath in audio_trim_filepaths:
        audio_trim_filename = audio_trim_filepath.split(os.path.sep)[-1]
        print('[INFO] reading already trimmed audio file: '+audio_trim_filename)
        sample_rate_trim, audio_trim = scipy.io.wavfile.read(audio_trim_filepath)
        duration_trim = audio_trim.shape[0] / sample_rate_trim
        print('[INFO] duration of the already trimmed file = {}'.format(duration_trim))
        
        extract_frame(audio_trim_filename, duration_trim, data_path, 1)
        extract_frame(audio_trim_filename, duration_trim, data_path, 2)   


def extract_frames_by_set(dataset_path, set_name):
    csv_filepaths = glob.glob('{}csvs{}{}_set{}fpc5{}*1.csv'.format(
        dataset_path,os.path.sep,set_name,os.path.sep,os.path.sep))
    csv_filepaths = csv_filepaths+ glob.glob('{}csvs{}{}_set{}fpc5{}*2.csv'.format(
        dataset_path,os.path.sep,set_name,os.path.sep,os.path.sep))
    
    for csv_filepath in csv_filepaths:
        csv_filename_split = csv_filepath.split(os.path.sep)[-1].split('_')
        trial_id = int(csv_filename_split[-1][-5])
        sub_id = int(csv_filename_split[1][3:])
        extract_frames_by_sub_trial(dataset_path, set_name, sub_id, trial_id)


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
        help="path to dataset")
ap.add_argument("-s", "--split", required = True,
        help="name the split train/valid/test")
ap.add_argument("-i", "--sub_info",  nargs='+', type=int,
        default = (0,0),
        help="subject info: ID, trial #")
args = vars(ap.parse_args())

sub_id_in = args["sub_info"][0]
trial_id_in = args["sub_info"][1]
set_name = args["split"]
dataset_path = args["dataset"]
print(dataset_path)
print(set_name)
print(sub_id_in, trial_id_in)
if (sub_id_in!=0 and trial_id_in!=0):
    extract_frames_by_sub_trial(dataset_path, set_name, sub_id_in, trial_id_in)
else:
    extract_frames_by_set(dataset_path, set_name)
