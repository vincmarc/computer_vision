import os
import numpy as np
from c3d import * 
from utils.visualization_util import * 

# PATHS: './video_paths.txt', cfg.C3D_info_path, cfg.path_all_videos
path_all_videos = cfg.path_all_videos

def run_c3d():
    '''
    1. './video_paths.txt' = file with all the 19 names of the folders that contain videos by category 
    2. cfg.C3D_info_path = file where num_frames_clips.txt is saved
    3. cfg.path_all_videos = folder that contains all the 19 subfolders with videos by category 
    '''
    num_clips_frames = []

    input_path = [line.strip() for line in open('./video_paths.txt', 'r')]
    input_path = [os.path.join(path_all_videos, i) for i in input_path]

    feat_output_path = [line.strip()+'_Features' for line in open('./video_paths.txt', 'r')]
    feat_output_path = [os.path.join(path_all_videos, i) for i in feat_output_path]
    
    assert len(input_path) == len(feat_output_path)

    for path in feat_output_path:
        if not os.path.exists(path):
            os.makedirs(path)

    print('C3D Features directories initialized')
    done_check = []

    for path in range(len(input_path)):
        for filename in os.listdir(input_path[path]):
            if filename.endswith('.mp4'):
                video_name = os.path.join(input_path[path], filename)       #Ex. path + Stealing002_x264.mp4
                name = os.path.basename(video_name).split('.')[0]           #Ex. Stealing002_x264

                # read video
                video_clips, num_frames = get_video_clips(video_name)
                print("Number of clips in the video : ", len(video_clips))
                num_clips_frames.append((video_name, num_frames, len(video_clips)))
                
                # initialize C3D model 
                feature_extractor = c3d_feature_extractor()
                
                # extract features
                rgb_features = []
                for i, clip in enumerate(video_clips):
                    clip = np.array(clip)
                    if len(clip) < params.frame_count:
                        continue

                    clip = preprocess_input(clip)
                    rgb_feature = feature_extractor.predict(clip)[0] # predict fc6 output using C3D weights
                    rgb_features.append(rgb_feature)
                    print("Processed clip : {} / {}".format(i, len(video_clips)))

                # bag features
                rgb_features = np.array(rgb_features)
                rgb_feature_bag = interpolate(rgb_features, params.features_per_bag)
                
                save_path = os.path.join(feat_output_path[path], name + '.txt')
                np.savetxt(save_path, rgb_feature_bag)
                done_check.append(video_name)
            
            # can save the names of those videos whose features have been already extracted
            #cat_1 = done_check[0].split('/')[-1].strip('mp4')
            #cat_2 = ''.join(filter(str.isalpha, cat_1))[:-1]
            #with open(os.path.join(cfg.C3D_info_path, 'done_check_'+cat_2+'.txt'), 'w') as f0: 
                #print(done_check, file=f0)

        # save as txt the num of frames and clips in each video 
        cat_0 = num_clips_frames[0][0].split('/')[-1].strip('mp4')
        cat = ''.join(filter(str.isalpha, cat_0))[:-1]
        with open(os.path.join(cfg.C3D_info_path, 'num_frames_clips_'+cat+'.txt'), 'w') as f: 
            print(num_clips_frames, file=f)


if __name__ == '__main__':
    run_c3d()