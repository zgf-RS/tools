import os

# 设置你的文件夹路径
folder_path = '/Users/zgf/Desktop/byd专项/0605/'

# 旧的前缀和新的前缀
old_prefix = 'beijing'
new_prefix = 'shenzhen'

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 检查文件名是否以旧前缀开始
    if filename.startswith(old_prefix):
        # 构建新的文件名
        new_filename = filename.replace(old_prefix, new_prefix)
        
        # 旧文件的完整路径和新文件的完整路径
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)
        
        # 重命名文件
        os.rename(old_file, new_file)
        print(f'文件已从 {filename} 重命名为 {new_filename}')