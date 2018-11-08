import keras.backend as K
from keras.layers import Dense, Input, Dropout
from keras.models import Sequential, Model

def DenoisingAutoencoder(input,target):
	Ninput = input.shape[1]
	Noutput = target.shape[1]
	hidden_dims = [1024,512,256]
	latent_dim = 128

	encodeInput = Input(shape=(Ninput,))
	encodeModel = Sequential([Dense(hidden_dims[0],activation='relu',input_dim=Ninput)])
	encodeModel.add(Dropout(0.25))
	[encodeModel.add(Dense(d,activation='relu')) for d in hidden_dims[1:]]
	encodeModel.add(Dropout(0.25))
	encodeModel.add(Dense(latent_dim))

	decodeInput = Input(shape=(latent_dim,))
	decodeModel = Sequential([Dense(hidden_dims[-1],activation='relu',input_dim=latent_dim)])
	encodeModel.add(Dropout(0.25))
	[decodeModel.add(Dense(d,activation='relu')) for d in reversed(hidden_dims[:-1])]
	encodeModel.add(Dropout(0.25))
	decodeModel.add(Dense(Noutput,activation='sigmoid'))

	encoded = encodeModel(encodeInput)
	decoded = decodeModel(decodeInput)

	encoder = Model(encodeInput,encoded)
	decoder = Model(decodeInput,decoded)

	aeOut = decoder(encoder(encodeInput))
	autoencoder = Model(encodeInput,aeOut)
	autoencoder.compile(loss='binary_crossentropy',optimizer='rmsprop')
	
	return autoencoder, encoder, decoder

def Classifier(X):

	input_dim = X.shape[1]

	clf = Sequential([
	    Dense(64,activation='relu',input_dim=input_dim),
	    Dropout(0.25),
	    Dense(16,activation='relu'),
	    Dropout(0.25),
	    Dense(5,activation='softmax')
	])

	clf.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

	return clf