import argparse
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint
import torch

from gemelli.datasets import CellPatchesDataset
from gemelli.dataloader import BalancedDataLoader
from gemelli.train import VggModule

parser = argparse.ArgumentParser()
parser = pl.Trainer.add_argparse_args(parser)
parser.add_argument('--use_mask',type=bool,default=False)
parser.add_argument('--fmaps',type=int,default=32)
parser.add_argument('--lr',type=float,default=1e-6)
parser.add_argument('--model_name',default=None)
args = parser.parse_args()

input_size=(128,128)
pretransform_input_size=(256,256)

train_dataset  = CellPatchesDataset('~/gemelli/dataset_info/0_train_samples.csv',input_size=pretransform_input_size,use_mask=args.use_mask,augment=True)
val_dataset = CellPatchesDataset('~/gemelli/dataset_info/0_val_samples.csv',input_size=input_size,use_mask=args.use_mask,augment=Falsed)

assert train_dataset.n_classes==val_dataset.n_classes
print(f'total classes: {train_dataset.n_classes}')

num_channels = train_dataset[0][0].shape[0]
print(f'input shape: {train_dataset[0][0].shape}')

model = VggModule(input_channels=num_channels, output_classes=train_dataset.n_classes, fmaps=args.fmaps, input_size=input_size, learning_rate=args.lr)

logger = TensorBoardLogger("logs",name=args.model_name)

checkpoint_callback = ModelCheckpoint(
        monitor='val_accuracy',
        filename='epoch{epoch:02d}-val_accuracy{val_accuracy:.2f}',
        auto_insert_metric_name=False,
        save_last=True,
        mode='max'
    )

trainer = pl.Trainer.from_argparse_args(args, logger=logger, callbacks=[checkpoint_callback])

trainer.fit(
    model,
    BalancedDataLoader(train_dataset, batch_size=32,num_workers=10),
    torch.utils.data.DataLoader(val_dataset, batch_size=32,num_workers=10)
)