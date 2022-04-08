import pandas as pd
from matplotlib import pyplot as plt
def visualize_plot(X, y, name): #시계열에 따른 예측도 시각화
    target = y
    pred = pd.Series(X, index=target.index)
    plt.figure(figsize=(12,10))
    pred.sort_index().plot(label='model')
    target.sort_index().plot(label='target')
    plt.suptitle(f'{name}',fontsize=20)
    mse = ((target - pred) ** 2).mean()
    plt.title(f'MSE is {mse:.1f}')
    plt.legend()