 for action_error in True False; do
 for add_anomaly in True False; do

    python cliport/anomaly_generator_stack_pyramid.py  task=stack-block-pyramid-seq-unseen-colors n=500 data_dir=/mnt/lynx4/users/zhang/yinxu/Workfolder/data/vlm add_action_error=$action_error add_anomaly=$add_anomaly

 done
 done