import torch
import torch.nn as nn

if torch.cuda.is_available():
	torch.set_default_tensor_type('torch.cuda.FloatTensor')
else:
	torch.set_default_tensor_type('torch.FloatTensor')

###### Pix2Pix Utilities ##########################################################

class downConv(nn.Module):
	def __init__(self, in_layer, out_layer, take_norm=True):
		super(downConv, self).__init__()
		self.conv = nn.Conv2d(in_layer, out_layer, kernel_size=4, stride=2, padding=1)
		self.act = nn.LeakyReLU(0.2, True)
		self.norm = nn.BatchNorm2d(out_layer)
		self.take_norm = take_norm

	def forward(self, x):
		x = self.conv(x)
		if self.take_norm:
			return self.act(self.norm(x))
		else :
			return self.act(x)

class upConv(nn.Module):
	def __init__(self, in_layer, out_layer):
		super(upConv, self).__init__()
		self.convt = nn.ConvTranspose2d(in_layer, out_layer, kernel_size=4, stride=2, padding=1)
		self.act = nn.ReLU(True)
		self.norm = nn.BatchNorm2d(out_layer)

	def forward(self, x):
		x = self.act(self.norm(self.convt(x)))
		return x

class Generator(nn.Module):
	def __init__(self, n_downsample=2, n_channels=3):
		super(Generator, self).__init__()
		model = [downConv(n_channels, 64, take_norm=False)]
		model += [downConv(64, 128)]
		model += [downConv(128, 256)]
		model += [downConv(256, 512)]
		for i in range(n_downsample):
			model += [downConv(512, 512)]

		for i in range(n_downsample):
			model += [upConv(512, 512)]

		model += [upConv(512, 256)]
		model += [upConv(256, 128)]
		model += [upConv(128, 64)]
		model += [nn.ConvTranspose2d(64, n_channels, kernel_size=4, stride=2, padding=1)]
		model += [nn.ReLU(True)]
		model += [nn.Tanh()]

		self.model = nn.Sequential(*model)

	def forward(self, x):
		return self.model(x)

class Discriminator(nn.Module):
	def __init__(self, n_channels=6):
		super(Discriminator, self).__init__()
		model = [downConv(n_channels, 64, take_norm=False)]
		model += [downConv(64, 128)]
		model += [downConv(128, 256)]
		model += [nn.Conv2d(256, 512, kernel_size=2, stride=1)]
		model += [nn.BatchNorm2d(512)]
		model += [nn.LeakyReLU(0.2, True)]
		model += [nn.Conv2d(512, 1, kernel_size=2, stride=1)]
		model += [nn.Sigmoid()]

		self.model = nn.Sequential(*model)

	def forward(self, inp, un):
		return self.model(torch.cat((inp, un), 1))




# if __name__ == '__main__':
# 	inp = torch.randn(1, 3, 256, 256)
# 	un = torch.randn(1, 3, 256, 256)
# 	model = Discriminator()
# 	# model2 = downConv(3, 64)
# 	# print(model)
# 	print(model(inp, un))	

#######################################################################################