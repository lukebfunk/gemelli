import argparse
import pytorch_lightning as pl
import torch
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint

from gemelli.datasets import CellPatchesDataset
from gemelli.dataloader import BalancedDataLoader
from gemelli.train import VggModule

parser = argparse.ArgumentParser()
parser = pl.Trainer.add_argparse_args(parser)
parser.add_argument('--input_size',type=int,default=256)
parser.add_argument('--use_mask',type=bool,default=False)
parser.add_argument('--lr',type=float,default=1e-5)
parser.add_argument('--model_name',default=None)
args = parser.parse_args()

input_size=(args.input_size,args.input_size)

train_dataset  = CellPatchesDataset('~/gemelli/dataset_info/0_train_samples.csv',input_size=input_size,use_mask=args.use_mask,augment=False)
val_dataset = CellPatchesDataset('~/gemelli/dataset_info/0_val_samples.csv',input_size=input_size,use_mask=args.use_mask,augment=False)

assert train_dataset.n_classes==val_dataset.n_classes

num_channels = train_dataset[0][0].shape[0]
print(f'input shape = {train_dataset[0][0].shape}')

# learning rate was previously hard coded to 1e-3
model = VggModule(input_channels=num_channels, output_classes=train_dataset.n_classes, input_size=input_size, learning_rate=args.lr)

print(model.learning_rate)

logger = TensorBoardLogger("logs",name=args.model_name)

checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',
        filename='epoch{epoch:02d}-val_accuracy{val_accuracy:.2f}',
        auto_insert_metric_name=False,
        save_last=True,
        # mode='max'
    )

trainer = pl.Trainer.from_argparse_args(args, logger=logger, callbacks=[checkpoint_callback], max_epochs=250)
print(f"Validation every {trainer.check_val_every_n_epoch} epochs")

trainer.fit(
    model,
    torch.utils.data.DataLoader(train_dataset, batch_size=16,num_workers=10,shuffle=True),
    torch.utils.data.DataLoader(val_dataset, batch_size=16,num_workers=10)
)