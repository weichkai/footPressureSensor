import pandas as pd
import numpy as np

# 读取 CSV 文件，跳过第一行
df = pd.read_csv('./b/test.csv', header=None, skiprows=1)

# 提取第1列的数据
column_data = df[0]

# 处理数据
data_list = []
for cell in column_data:
    # 以逗号分隔
    parts = cell.split(',')
    # 确保提取的部分是有效的数字
    try:
        # 提取第6个到最后一个数字，并过滤掉非数字
        numbers = [int(x) for x in parts[5:] if x.isdigit()]
        data_list.append(numbers)
    except ValueError:
        # 如果遇到非数字的情况，可以选择跳过或处理
        print(f"Skipping invalid data: {cell}")

# 将数据转换为 np.array
data_array = np.array(data_list, dtype=int)

# 打印结果
print(data_array)
print(data_array.shape)


import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import matplotlib.animation as animation

# 假设这里是从CSV中读取的示例数据
data_list = data_array

# 转换数据集
zoom_factor = 3
vmin, vmax = 1, 100

def process_data(data):
    try:
        matrix = np.array(data).reshape((16, 13))
        matrix = zoom(matrix, zoom_factor)
        matrix[matrix < 5] = 0
        masked_matrix = np.ma.masked_where(matrix == 0, matrix)
        return masked_matrix
    except Exception as e:
        print(f"Error processing data: {e}")
        return np.ma.masked_array(np.zeros((16 * zoom_factor, 13 * zoom_factor)), mask=True)

# 处理数据
try:
    processed_datasets = [process_data(data) for data in data_list]
    print(f"Number of processed datasets: {len(processed_datasets)}")
    if len(processed_datasets) > 0:
        print(f"Shape of first dataset: {processed_datasets[0].shape}")
    else:
        print("No datasets processed.")
except Exception as e:
    print(f"Error processing datasets: {e}")

# 创建图形对象
fig, ax = plt.subplots()
cmap = plt.cm.jet
cmap.set_bad(color='white')

if len(processed_datasets) > 0:
    # 初始化图像
    im = ax.imshow(processed_datasets[0], origin='lower', interpolation='nearest', vmin=vmin, vmax=vmax, cmap=cmap)
    cbar = fig.colorbar(im, ax=ax, extend='both', ticks=np.linspace(vmin, vmax, num=8))

    # 初始化函数
    def init():
        im.set_data(processed_datasets[0])
        return [im]

    # 动画函数
    def animate(i):
        im.set_data(processed_datasets[i])
        return [im]

    # 创建动画
    ani = animation.FuncAnimation(fig, animate, frames=len(processed_datasets), init_func=init, interval=50, blit=True)

    # 显示动画
    plt.show()
else:
    print("No data available to animate.")
