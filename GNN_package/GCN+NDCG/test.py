from types import prepare_class
import torch

import numpy as np
import torch.nn as nn
import torch.optim as optim
from GraphSage import GraphSage
from data import GraphData
from sample import multihop_sampling
from sklearn.metrics import hamming_loss


from collections import namedtuple



