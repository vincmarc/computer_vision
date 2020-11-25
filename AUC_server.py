import numpy as np
import os
from utils.visualization_util import *
from sklearn import metrics

# PATHS: cfg.path_all_features, cfg.Ann_path, cfg.NamesAnn_path, './num_frames.txt'
# VARIABLES: cfg.train_exp_name, cfg.use_i3d

path_all_features = cfg.path_all_features
experiment_name = cfg.train_exp_name

# Score is a folder in path_all_features, created by test_detect_server.py, that contains 310 txt files of scores
score_path = os.path.join(path_all_features, 'Scores_'+experiment_name)

no_video = 1
frm_counter = 0
All_Detect = np.zeros(1000000)
All_GT = np.zeros(1000000)

all_annotations = [line.strip().split() for line in open(cfg.Ann_path, 'r')]
all_annotations_dict = {l[0].split('.')[0]:l[-4:] for l in all_annotations}

all_frames = [i.strip().split() for i in open('./num_frames.txt', 'r')]
assert [len(l) == 2 for l in all_frames]
all_frames_dict = {l[0]:l[1:] for l in all_frames}

all_ann_names = [line.strip().replace('.mp4', '.txt').replace('/', '_Features/') for line in open(cfg.NamesAnn_path, 'r')]
if cfg.use_i3d: 
   all_ann_names = [line.strip().replace('.mp4', '.txt').replace('/', '_Features_I3D/') for line in open(cfg.NamesAnn_path, 'r')]

for filename in all_ann_names:
   if filename.endswith('.txt'):
      video_name = os.path.join(path_all_features, filename)
      name = os.path.basename(video_name).split('.')[0]
      print(name)
      name_txt = name + '.txt'
      
      scores = os.path.join(score_path, name_txt)
      score = [line.strip() for line in open(scores, 'r')]
      # list of 32 str (each str contains 1 score) 

      C3D_file = [line.strip() for line in open(video_name, 'r')]
      # list of 32 str (each str contains 4096 floats)

      Ann = all_annotations_dict[name] 
      # list of 4 str (each str contains 1 annot as str)

      # read video
      num_frames = all_frames_dict[filename]
      
      # assign to each frame the anomaly score of the feature it belongs to
      num_features = len(C3D_file)     # must be 32
      num_frames_C3D = num_features*16 # as the features were computed for every 16 frames
      Detection_score_32shots = np.zeros(num_frames_C3D)
      Thirty2_shots = np.round(np.linspace(0, num_features, 32))

      l = range(len(Thirty2_shots))
      p_c = -1
      for c_shots, n_shots in zip (l, l[1:]):
         p_c = p_c + 1
         ss = Thirty2_shots[c_shots]
         ee = Thirty2_shots[n_shots] - 1
         print('ss:', ss, 'ee:', ee)
         print('c_shots:', c_shots, 'n_shots:', n_shots)

         if c_shots == len(Thirty2_shots):
            ee=Thirty2_shots[n_shots]

         if ee < ss:
            Detection_score_32shots[(int(ss))*16:(int(ss))*16+16+1] = score[p_c]
            print(ee < ss)
         else:
            Detection_score_32shots[(int(ss))*16:(int(ee))*16+16+1] = score[p_c]
            print(ee > ss)

      Final_score = np.append(Detection_score_32shots, np.repeat(Detection_score_32shots[-1], [num_frames-len(Detection_score_32shots)]))
      GT = np.zeros(num_frames)

      # check the temporal annotation
      t_txt = [int(i) for i in Ann]
      
      for y in range(0,3,2):
         if t_txt[y] >= 0:
            st_fr = max(int(float(t_txt[y])), 0)
            end_fr = min(int(float(t_txt[y+1])), num_frames)
            GT[st_fr:end_fr+1] = 1

      All_Detect[frm_counter:frm_counter+len(Final_score)] = Final_score
      All_GT[frm_counter:frm_counter+len(Final_score)] = GT
      print('Video ', no_video, ' successfully processed!')
      no_video = no_video + 1
      frm_counter = frm_counter+len(Final_score)

All_Detect = (All_Detect[0:frm_counter])
All_GT = All_GT[0:frm_counter]
tot_scores = All_Detect
si = tot_scores.argsort()[::-1]
tp = All_GT[si] > 0
fp = All_GT[si] == 0
tp = np.cumsum(tp)
fp = np.cumsum(fp)
nrpos = sum(All_GT)
rec = tp / nrpos
fpr = fp / sum(All_GT == 0)
prec = tp / (fp + tp)
AUC1 = np.trapz(rec, fpr)
print('AUC1: ', AUC1)

fpr, tpr, thresholds = metrics.roc_curve(All_GT, All_Detect)
AUC2 = metrics.auc(fpr, tpr)
print('AUC2: ', AUC2)